# MIT License
#
# Copyright (c) 2025 XianYin69
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# 文件名: 晶体管共射极放大电路.py
# 功能: 计算晶体管共射极放大电路的直流工作点和交流小信号参数。
# 注意: 本程序仅适用于分析典型的晶体管共射极放大电路，不适用于其他复杂电路或特殊情况。
#      电阻输入部分的代码逻辑是计算并联等效电阻，请根据实际电路图确认是否适用。

from typing import List # 导入 List 用于类型批注
import math # 导入 math 模块用于检查 nan 和 inf

# 定义一个函数来获取有效的浮点数输入
def get_float_input(prompt: str) -> float:
    """获取一个有效的浮点数输入，直到用户输入有效值为止。"""
    while True:
        try:
            value = float(input(prompt))
            return value
        except ValueError:
            print("输入无效，请输入一个数字。")

# 定义一个函数来获取有效的整数输入
def get_int_input(prompt: str) -> int:
    """获取一个有效的整数输入，直到用户输入有效值为止。"""
    while True:
        try:
            value = int(input(prompt))
            return value
        except ValueError:
            print("输入无效，请输入一个整数。")

# 定义一个函数来获取有效的 'y' 或 'N' 输入
def get_yes_no_input(prompt: str, default: str = 'N') -> str:
    """获取一个有效的 'y' 或 'N' 输入，默认为指定值。"""
    while True:
        user_input = input(prompt).strip().lower()
        if user_input == 'y':
            return 'y'
        elif user_input == 'n' or user_input == '':
            return 'n'
        else:
            print("输入无效，请输入 'y' 或 'N'。")

print("注意！！！本程序仅适用于晶体管共射放大电路！！！")

# --- 输入直流参数 ---
print("\n--- 请输入直流参数 ---")

# 获取电源电压 Vcc
Vcc: float = get_float_input("Vcc(V) = ")

# 获取晶体管的直流电流放大系数 beta
Transistor_beta: float = get_float_input("beta = ")

# 获取负载电阻 RL
Rl: float = get_float_input("RL(kOhm)(// 10 ^ 3) = ")

# 获取基极偏置电阻 Rb 的组成和值
RbUpValueLst: List[float] = [] # 存储基极上半部分电阻值（与Vcc相连）
RbDownValueLst: List[float] = [] # 存储基极下半部分电阻值（与地相连）

# 询问 Rb 是否由多个电阻组成 (分压偏置)
RbCompnented: str = get_yes_no_input("Rb是否是由一个或多个电阻组成？(y 或 N)(默认为N)")

# 初始化用于计算等效 Rb 的变量
SumRbUp_reciprocal: float = 0.0
SumRbDown_reciprocal: float = 0.0
RbValue: float = float('inf') # 默认基极电阻无穷大
single_Rb_input: str = 'n' # 初始化 single_Rb_input 变量

if RbCompnented == 'y':
    # 获取基极上半部分电阻数量和值
    upPartNum: int = get_int_input("请输入基极上半部分的电阻数量（与基极和直流电源相连的电阻）：")
    for i in range(upPartNum):
        Rbu: float = get_float_input(f"Rb_up{i+1}(kOhm)(// 10 ^ 3) = ")
        RbUpValueLst.append(Rbu)

    # 获取基极下半部分电阻数量和值
    downPartNum: int = get_int_input("请输入基极下半部分的电阻数量（与基极相连并接地的电阻）：")
    for i in range(downPartNum):
        Rbd: float = get_float_input(f"Rb_down{i+1}(kOhm)(// 10 ^ 3) = ")
        RbDownValueLst.append(Rbd)

    # 计算基极偏置电阻的等效电阻 (此处代码逻辑计算的是上下偏置电阻并联后的等效电阻)
    # 请根据实际电路图确认此计算逻辑是否正确，典型的分压偏置电路中，Rb等效电阻应为上下电阻的并联。
    SumRbUp_reciprocal = sum(1 / r for r in RbUpValueLst) if RbUpValueLst else 0.0
    SumRbDown_reciprocal = sum(1 / r for r in RbDownValueLst) if RbDownValueLst else 0.0

    # 避免除以零的情况
    if SumRbUp_reciprocal == 0.0 and SumRbDown_reciprocal == 0.0:
        RbValue = 0.0 # 没有偏置电阻
    elif SumRbUp_reciprocal == 0.0:
         # 只有下偏置电阻，等效电阻为下偏置电阻并联值
        RbValue = 1 / SumRbDown_reciprocal if SumRbDown_reciprocal != 0.0 else float('inf') # 无穷大电阻
    elif SumRbDown_reciprocal == 0.0:
         # 只有上偏置电阻，等效电阻为上偏置电阻并联值
        RbValue = 1 / SumRbUp_reciprocal if SumRbUp_reciprocal != 0.0 else float('inf') # 无穷大电阻
    else:
        # 上下偏置电阻都有，计算它们并联后的等效电阻
        RbValue = 1 / (SumRbUp_reciprocal + SumRbDown_reciprocal)

else:
    # 如果不是 'y'，则询问用户是否输入单个 Rb 值。
    single_Rb_input = get_yes_no_input("是否输入单个基极电阻 Rb？(y 或 N)(默认为N)")
    if single_Rb_input == 'y':
        RbValue = get_float_input("Rb(kOhm)(// 10 ^ 3) = ")
    else:
        # 假定 Rb 无穷大 (例如基极直接连接到信号源，没有偏置电阻)
        # 这可能导致 Ib 为 0，Ic 为 0，Vce 接近 Vcc，具体取决于电路连接。
        # 在此程序中，为了避免除以零，我们将其设置为一个非常大的值来模拟无穷大。
        RbValue = float('inf')
        print("提示：没有输入基极电阻，假定等效基极电阻 Rb 为无穷大。")


# 获取集电极电阻 Rc 的组成和值
RcValueLst: List[float] = [] # 存储集电极电阻值

# 询问 Rc 是否由多个电阻组成 (并联)
RcCompnent: str = get_yes_no_input("Rc是否由非零个电阻组成？（y 或 N）（默认为N）")

# 初始化集电极等效电阻变量
RcValue_eq: float = 0.0 # 默认 Rc 为 0

if RcCompnent == 'y':
    # 获取集电极电阻数量和值
    RcNum: int = get_int_input("请输入与集电极连接的电阻数量：")
    if RcNum > 0:
        for i in range(RcNum):
            RcValue: float = get_float_input(f"Rc{i+1}(kOhm)(// 10 ^ 3) = ")
            RcValueLst.append(RcValue)

    # 计算集电极等效电阻 (此处代码逻辑计算的是并联等效电阻)
    SumRc_reciprocal: float = sum(1 / r for r in RcValueLst) if RcValueLst else 0.0
    RcValue_eq = 1 / SumRc_reciprocal if SumRc_reciprocal != 0.0 else float('inf') # 避免除以零
else:
    # 如果不是 'y'，则询问用户是否输入单个 Rc 值。
    single_Rc_input: str = get_yes_no_input("是否输入单个集电极电阻 Rc？(y 或 N)(默认为N)")
    if single_Rc_input == 'y':
        RcValue_eq = get_float_input("Rc(kOhm)(// 10 ^ 3) = ")
    else:
        # 假定 Rc 为 0 (例如集电极直接连接到电源，没有电阻)
        RcValue_eq = 0.0
        print("提示：没有输入集电极电阻，假定等效集电极电阻 Rc 为 0。")


# 获取发射极电阻 Re 的组成和值
ReValueLst: List[float] = [] # 存储发射极电阻值

# 询问 Re 是否由多个电阻组成 (并联)
ReCompnent: str = get_yes_no_input("Re是否由非零个电阻组成？（y 或 N）（默认为N）")

# 初始化发射极等效电阻变量
ReValue_eq: float = 0.0 # 默认 Re 为 0

if ReCompnent == 'y':
    # 获取发射极电阻数量和值
    ReNum: int = get_int_input("请输入与发射极连接的电阻数量：")
    if ReNum > 0:
        for i in range(ReNum):
            ReValue: float = get_float_input(f"Re{i+1}(kOhm)(// 10 ^ 3) = ")
            ReValueLst.append(ReValue)

    # 计算发射极等效电阻 (此处代码逻辑计算的是并联等效电阻)
    SumRe_reciprocal: float = sum(1 / r for r in ReValueLst) if ReValueLst else 0.0
    ReValue_eq = 1 / SumRe_reciprocal if SumRe_reciprocal != 0.0 else float('inf') # 避免除以零
else:
    # 如果不是 'y'，则询问用户是否输入单个 Re 值。
    single_Re_input: str = get_yes_no_input("是否输入单个发射极电阻 Re？(y 或 N)(默认为N)")
    if single_Re_input == 'y':
        ReValue_eq = get_float_input("Re(kOhm)(// 10 ^ 3) = ")
    else:
        # 假定 Re 为 0 (例如发射极直接接地，没有电阻)
        ReValue_eq = 0.0
        print("提示：没有输入发射极电阻，假定等效发射极电阻 Re 为 0。")


# 获取晶体管的种类以确定 Vbe (基极-发射极电压)
Vbe: float = 0.0 # 初始化 Vbe
while True:
    Transistor_Type: int = get_int_input("请输入晶体管的种类（硅管 ： 1 锗管 ： 2）：")
    if Transistor_Type == 1:
        Vbe = 0.6 # 硅管 Vbe 压降
        break
    elif Transistor_Type == 2:
        Vbe = 0.2 # 锗管 Vbe 压降
        break
    else:
        print("输入无效，请重新输入 1 或 2。")

# --- 计算直流工作点 ---
print("\n--- 计算直流工作点 ---")

# 初始化直流工作点参数变量
Vb: float = float('nan')
Ib: float = float('nan')
Ic: float = float('nan')
Ie: float = float('nan')
Vce: float = float('nan')


# 计算基极电压 Vb
# 对于分压偏置电路，Vb = Vcc * (Rb_down_eq / (Rb_up_eq + Rb_down_eq))
if RbCompnented == 'y':
     # 计算上偏置电阻的并联等效值
    Rb_up_eq: float = 1 / SumRbUp_reciprocal if SumRbUp_reciprocal != 0.0 else float('inf')
    # 计算下偏置电阻的并联等效值
    Rb_down_eq: float = 1 / SumRbDown_reciprocal if SumRbDown_reciprocal != 0.0 else float('inf')

    # 计算基极电压 Vb 的分压比
    if math.isinf(Rb_up_eq) and math.isinf(Rb_down_eq):
        Vb = float('nan') # 无法确定 Vb
        print("警告：上下偏置电阻都为无穷大，无法确定基极电压 Vb。")
    elif math.isinf(Rb_up_eq):
        Vb = Vcc # 上偏置开路，Vb 接近 Vcc
    elif math.isinf(Rb_down_eq):
        Vb = 0.0 # 下偏置开路，Vb 接近地
    elif (Rb_up_eq + Rb_down_eq) == 0.0:
         Vb = float('nan') # 分母为零
         print("警告：上下偏置电阻和为零，无法计算基极电压 Vb。")
    else:
        Vb = Vcc * (Rb_down_eq / (Rb_up_eq + Rb_down_eq))

elif single_Rb_input == 'y':
    # 如果是单个 Rb 电阻接 Vcc 的情况，使用近似公式计算 Vb。
    if (RbValue + (1 + Transistor_beta) * ReValue_eq) != 0.0:
         Ib_approx: float = (Vcc - Vbe) / (RbValue + (1 + Transistor_beta) * ReValue_eq)
         Vb = Vcc - Ib_approx * RbValue
    else:
         Vb = float('nan') # 分母为零
         print("警告：计算近似基极电流时分母为零，无法计算基极电压 Vb。")
# else 分支对应 RbValue = float('inf') 的情况，Vb 已经在初始化时假定为 Vcc，此处无需额外处理。


# 计算发射极电压 Ve
Ve = Vb - Vbe

# 计算发射极电流 Ie
# Ie = Ve / ReValue_eq
if ReValue_eq != 0.0 and not math.isinf(ReValue_eq):
    Ie = Ve / ReValue_eq
elif math.isinf(ReValue_eq):
     Ie = 0.0 # 如果 Re 无穷大，Ie 为 0
else: # ReValue_eq == 0.0
    Ie = float('inf') if Ve > 0.0 else (0.0 if Ve == 0.0 else float('nan')) # 如果 Re=0 且 Ve>0，电流无穷大；如果 Ve=0，电流为0；否则无法确定
    if ReValue_eq == 0.0:
        print("警告：发射极电阻 Re 为零，发射极电流 Ie 可能为无穷大、零或无法确定。")


# 计算集电极电流 Ic 和基极电流 Ib
# 使用 Ie 计算 Ic 更直接： Ic = Ie * (beta / (1 + beta))
# Ib = Ie / (1 + beta)
if not math.isnan(Ie) and not math.isinf(Ie):
    Ic = Ie * (Transistor_beta / (1 + Transistor_beta))
    Ib = Ie / (1 + Transistor_beta)
else:
    Ic = float('nan')
    Ib = float('nan')
    if math.isinf(Ie):
         print("警告：发射极电流 Ie 为无穷大，无法计算集电极电流 Ic 和基极电流 Ib。")
    else:
         print("警告：无法计算发射极电流 Ie，无法计算集电极电流 Ic 和基极电流 Ib。")


# 计算集电极-发射极电压 Vce
# Vce = Vcc - Ic * RcValue_eq - Ie * ReValue_eq
if not math.isnan(Ic) and not math.isnan(Ie):
     Vce = Vcc - Ic * RcValue_eq - Ie * ReValue_eq
else:
    Vce = float('nan')
    print("警告：无法计算集电极电流 Ic 和发射极电流 Ie，无法计算集电极-发射极电压 Vce。")


# 输出直流工作点结果
print(f"\n直流工作点参数：")
# 使用 isnan() 检查是否为 NaN，使用 isinf() 检查是否为 Infinity
print(f"基极电压 Vb = {'NaN' if math.isnan(Vb) else f'{Vb:.4f} V'}")
print(f"发射极电压 Ve = {'NaN' if math.isnan(Ve) else f'{Ve:.4f} V'}")
print(f"集电极电流 Ic = {'NaN' if math.isnan(Ic) else (f'{Ic:.4f} mA' if not math.isinf(Ic) else 'Infinity mA')}") # 假设电流单位是 mA (电阻单位 kOhm, 电压单位 V)
print(f"基极电流 Ib = {'NaN' if math.isnan(Ib) else (f'{Ib:.4f} mA' if not math.isinf(Ib) else 'Infinity mA')}")   # 假设电流单位是 mA
print(f"发射极电流 Ie = {'NaN' if math.isnan(Ie) else (f'{Ie:.4f} mA' if not math.isinf(Ie) else 'Infinity mA')}") # 假设电流单位是 mA
print(f"集电极-发射极电压 Vce = {'NaN' if math.isnan(Vce) else f'{Vce:.4f} V'}")


# --- 计算交流特性 (可选) ---
print("\n--- 计算交流特性 ---")

# 询问是否需要计算交流特性
acPart: str = get_yes_no_input("是否需要计算交流特性（y 或 N）（默认为N）:")

if acPart == 'y':
    # 获取晶体管的体电阻 rbb'
    rbb: float = get_float_input("rbb'(kOhm)(// 10 ^ 3) = ")

    # 计算晶体管的输入电阻 rbe
    # rbe = rbb' + (1 + beta) * (Vt / Ic)
    # 其中 Vt 是热电压，约等于 26mV (0.026V) 在室温下。
    rbe: float = float('inf') # 初始化 rbe
    if Ic > 0.0 and not math.isinf(Ic) and not math.isnan(Ic):
         rbe = rbb + (1 + Transistor_beta) * (0.026 / Ic)
    else:
         rbe = float('inf') # 如果 Ic <= 0 或无穷大/NaN，rbe 趋近无穷大
         print("警告：直流集电极电流 Ic 小于等于零、无穷大或无法确定，交流输入电阻 rbe 趋近无穷大。")


    # 询问交流通路下发射极与公共接地之间是否有电阻
    ReIdentify: str = get_yes_no_input("在交流通路下发射极与公共接地之间是否有电阻？（y 或 N）（默认为N）")

    # 计算交流小信号参数 (电压增益 Au, 输入电阻 Ri, 输出电阻 Ro)

    # 计算交流负载电阻 RoSum (集电极电阻 RcValue_eq 与负载电阻 Rl 的并联)
    RoSum: float = float('nan') # 初始化 RoSum
    if not (math.isnan(RcValue_eq) or math.isnan(Rl) or (math.isinf(RcValue_eq) and math.isinf(Rl))):
        # 处理无穷大的并联
        if math.isinf(RcValue_eq):
            RoSum = Rl
        elif math.isinf(Rl):
            RoSum = RcValue_eq
        elif (RcValue_eq + Rl) != 0.0:
            RoSum = (RcValue_eq * Rl) / (RcValue_eq + Rl)
        else:
            RoSum = float('nan') # 分母为零
            print("警告：计算交流负载电阻时分母为零，RoSum 无法确定。")
    else:
        print("警告：集电极电阻 Rc 或负载电阻 Rl 无效，RoSum 无法确定。")


    Au: float = float('nan') # 初始化 Au
    Ri: float = float('nan') # 初始化 Ri
    Ro: float = float('nan') # 初始化 Ro

    if ReIdentify == 'n':
        # 交流通路下发射极直接接地 (ReValue_eq 不影响交流特性)
        print("交流通路下发射极直接接地。")

        # 计算电压增益 Au
        # Au = - beta * (RoSum / rbe)
        if not math.isnan(RoSum) and not math.isinf(rbe) and rbe != 0.0:
            Au = -(Transistor_beta * RoSum) / rbe
        else:
            Au = float('nan') # 分母为零 或 rbe 无穷大/NaN，或 RoSum 为 NaN


        # 计算输入电阻 Ri
        # Ri = RbValue 并联 rbe = (RbValue * rbe) / (RbValue + rbe)
        if not (math.isnan(RbValue) or math.isnan(rbe) or (math.isinf(RbValue) and math.isinf(rbe))):
             # 处理无穷大的并联：如果一个无穷大，结果是另一个；如果都无穷大，结果无穷大
             if math.isinf(RbValue):
                 Ri = rbe
             elif math.isinf(rbe):
                 Ri = RbValue
             elif (RbValue + rbe) != 0.0:
                 Ri = (RbValue * rbe) / (RbValue + rbe)
             else:
                 Ri = float('nan') # 分母为零
        else:
             Ri = float('nan') # RbValue 或 rbe 为 NaN


        # 计算输出电阻 Ro
        # Ro = RcValue_eq (不考虑晶体管输出电阻 ro)
        Ro = RcValue_eq

    else:
        # 交流通路下发射极有电阻 (ReValue_eq 影响交流特性)
        print("交流通路下发射极有电阻。")

        # 获取交流通路下发射极电阻的值 (注意与直流 ReValue_eq 可能不同，例如 Re 被电容旁路一部分)
        Re_ac_ValueLst: List[float] = []
        Re_ac_Num: int = get_int_input("请输入交流通路下与发射极连接的电阻数量：")
        if Re_ac_Num > 0:
            for i in range(Re_ac_Num):
                Re_ac_Value: float = get_float_input(f"Re_ac{i+1}(kOhm)(// 10 ^ 3) = ")
                Re_ac_ValueLst.append(Re_ac_Value)

        # 计算交流通路下发射极等效电阻 (此处代码逻辑计算的是串联等效电阻)
        Re_ac_eq: float = sum(Re_ac_ValueLst) if Re_ac_ValueLst else 0.0


        # 计算电压增益 Au
        # Au = - beta * RoSum / (rbe + (1 + beta) * Re_ac_eq)
        Au_denominator: float = rbe + (1 + Transistor_beta) * Re_ac_eq
        if not math.isnan(RoSum) and not math.isinf(Au_denominator) and Au_denominator != 0.0:
            Au = -(Transistor_beta * RoSum) / Au_denominator
        else:
             Au = float('nan') # 分母为零 或无穷大，或 RoSum 为 NaN


        # 计算输入电阻 Ri
        # Ri = RbValue 并联 (rbe + (1 + beta) * Re_ac_eq)
        Ri_parallel_term: float = rbe + (1 + Transistor_beta) * Re_ac_eq
        if not (math.isnan(RbValue) or math.isnan(Ri_parallel_term) or (math.isinf(RbValue) and math.isinf(Ri_parallel_term))):
             # 处理无穷大的并联
             if math.isinf(RbValue):
                 Ri = Ri_parallel_term
             elif math.isinf(Ri_parallel_term):
                 Ri = RbValue
             elif (RbValue + Ri_parallel_term) != 0.0:
                 Ri = (RbValue * Ri_parallel_term) / (RbValue + Ri_parallel_term)
             else:
                 Ri = float('nan') # 分母为零
        else:
             Ri = float('nan') # RbValue 或 Ri_parallel_term 为 NaN


        # 计算输出电阻 Ro
        # Ro = RcValue_eq (不考虑晶体管输出电阻 ro)
        Ro = RcValue_eq


    # 输出交流特性结果
    print("\n交流特性参数：")
    print(f"交流输入电阻 rbe = {'NaN' if math.isnan(rbe) else (f'{rbe:.4f} kOhm' if not math.isinf(rbe) else 'Infinity kOhm')}")
    # 判断 Au, Ri, Ro 是否是有效数字，避免输出 nan 或 inf
    print(f"电压增益 Au = {'NaN' if math.isnan(Au) else (f'{Au:.4f}' if not math.isinf(Au) else ('Infinity' if Au == float('inf') else '-Infinity'))}")

    print(f"输入电阻 Ri = {'NaN' if math.isnan(Ri) else (f'{Ri:.4f} kOhm' if not math.isinf(Ri) else 'Infinity kOhm')}")

    print(f"输出电阻 Ro = {'NaN' if math.isnan(Ro) else (f'{Ro:.4f} kOhm' if not math.isinf(Ro) else 'Infinity kOhm')}")


# 程序结束提示
print("\n程序运行完毕。")