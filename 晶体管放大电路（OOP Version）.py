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

# 文件名: 晶体管放大电路（OOP Version）.py
# 功能: 使用面向对象思想计算晶体管共射极放大电路的直流工作点和交流小信号参数。
# 注意: 本程序仅适用于分析典型的晶体管共射极放大电路，不适用于其他复杂电路或特殊情况。

from typing import List, Optional
import math

# 定义输入辅助函数
def get_float_input(prompt: str) -> float:
    """获取一个有效的浮点数输入，直到用户输入有效值为止。"""
    while True:
        try:
            value = float(input(prompt))
            return value
        except ValueError:
            print("输入无效，请输入一个数字。")

def get_int_input(prompt: str) -> int:
    """获取一个有效的整数输入，直到用户输入有效值为止。"""
    while True:
        try:
            value = int(input(prompt))
            return value
        except ValueError:
            print("输入无效，请输入一个整数。")

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

class Resistor:
    """表示电阻或电阻组合的类。"""
    def __init__(self, name: str, values: Optional[List[float]] = None, is_parallel: bool = True):
        self.name = name
        self.values = values if values is not None else []
        self.is_parallel = is_parallel # True 表示并联，False 表示串联
        self.equivalent_value: float = 0.0

    def calculate_equivalent(self) -> float:
        """计算电阻组合的等效电阻。"""
        if not self.values:
            self.equivalent_value = 0.0 if not self.is_parallel else float('inf') # 并联无电阻为无穷大，串联无电阻为0
            return self.equivalent_value

        if self.is_parallel:
            # 计算并联等效电阻
            sum_reciprocal = sum(1 / r for r in self.values if r != 0)
            self.equivalent_value = 1 / sum_reciprocal if sum_reciprocal != 0.0 else float('inf')
        else:
            # 计算串联等效电阻
            self.equivalent_value = sum(self.values)

        return self.equivalent_value

    def get_input(self):
        """获取电阻值输入。"""
        compnented = get_yes_no_input(f"'{self.name}' 是否由非零个电阻组成？（y 或 N）（默认为N）")
        if compnented == 'y':
            num = get_int_input(f"请输入与 '{self.name}' 连接的电阻数量：")
            if num > 0:
                for i in range(num):
                    value = get_float_input(f"{self.name}{i+1}(kOhm)(// 10 ^ 3) = ")
                    self.values.append(value)
        else:
            single_input = get_yes_no_input(f"是否输入单个电阻 '{self.name}' 的值？(y 或 N)(默认为N)")
            if single_input == 'y':
                value = get_float_input(f"{self.name}(kOhm)(// 10 ^ 3) = ")
                self.values.append(value)
            else:
                 # 根据并联或串联设置默认值
                 if self.is_parallel:
                     # 并联没有电阻，等效电阻无穷大
                     self.equivalent_value = float('inf')
                     print(f"提示：没有输入 '{self.name}' 电阻，假定等效电阻为无穷大。")
                 else:
                     # 串联没有电阻，等效电阻为0
                     self.equivalent_value = 0.0
                     print(f"提示：没有输入 '{self.name}' 电阻，假定等效电阻为 0。")


class Transistor:
    """表示晶体管的类。"""
    def __init__(self):
        self.beta: float = 0.0
        self.vbe: float = 0.0
        self.rbb_prime: float = 0.0
        self.rbe: float = float('inf') # 交流输入电阻

    def get_dc_parameters_input(self):
        """获取晶体管直流参数输入。"""
        self.beta = get_float_input("beta = ")
        while True:
            transistor_type = get_int_input("请输入晶体管的种类（硅管 ： 1 锗管 ： 2）：")
            if transistor_type == 1:
                self.vbe = 0.6 # 硅管 Vbe 压降
                break
            elif transistor_type == 2:
                self.vbe = 0.2 # 锗管 Vbe 压降
                break
            else:
                print("输入无效，请重新输入 1 或 2。")

    def get_ac_parameters_input(self):
        """获取晶体管交流参数输入。"""
        self.rbb_prime = get_float_input("rbb'(kOhm)(// 10 ^ 3) = ")

    def calculate_rbe(self, ic_ma: float):
        """计算交流输入电阻 rbe (kOhm)。"""
        # rbe = rbb' + (1 + beta) * (Vt / Ic)
        # 其中 Vt 是热电压，约等于 26mV (0.026V) 在室温下。
        # 注意：Ic 单位为 mA，Vt 单位为 V，rbe 单位为 kOhm。
        # 0.026V / Ic(mA) 得到的结果单位是 kOhm。
        vt = 0.026
        if ic_ma > 0.0 and not math.isinf(ic_ma) and not math.isnan(ic_ma):
             self.rbe = self.rbb_prime + (1 + self.beta) * (vt / ic_ma)
        else:
             self.rbe = float('inf') # 如果 Ic <= 0 或无穷大/NaN，rbe 趋近无穷大
             print("警告：直流集电极电流 Ic 小于等于零、无穷大或无法确定，交流输入电阻 rbe 趋近无穷大。")


class CommonEmitterAmplifier:
    """表示共射极放大电路的类。"""
    def __init__(self):
        self.vcc: float = 0.0
        self.rl: float = 0.0
        self.rb_up: Resistor = Resistor("基极上半部分电阻", is_parallel=True)
        self.rb_down: Resistor = Resistor("基极下半部分电阻", is_parallel=True)
        self.rc: Resistor = Resistor("集电极电阻", is_parallel=True)
        self.re_dc: Resistor = Resistor("发射极直流电阻", is_parallel=True)
        self.re_ac: Resistor = Resistor("发射极交流电阻", is_parallel=False) # 交流通路下发射极电阻通常是串联的
        self.transistor: Transistor = Transistor()

        # 直流工作点参数
        self.vb: float = float('nan')
        self.ve: float = float('nan')
        self.ib: float = float('nan')
        self.ic: float = float('nan')
        self.ie: float = float('nan')
        self.vce: float = float('nan')

        # 交流特性参数
        self.ro_sum: float = float('nan') # 交流负载电阻
        self.au: float = float('nan') # 电压增益
        self.ri: float = float('nan') # 输入电阻
        self.ro: float = float('nan') # 输出电阻


    def get_parameters_input(self):
        """获取电路所有参数输入。"""
        print("注意！！！本程序仅适用于晶体管共射放大电路！！！")

        # --- 输入直流参数 ---
        print("\n--- 请输入直流参数 ---")

        self.vcc = get_float_input("Vcc(V) = ")
        self.transistor.get_dc_parameters_input()
        self.rl = get_float_input("RL(kOhm)(// 10 ^ 3) = ")

        # 获取基极偏置电阻 Rb 的组成和值
        rb_compnented = get_yes_no_input("Rb是否是由一个或多个电阻组成？(y 或 N)(默认为N)")
        if rb_compnented == 'y':
            self.rb_up.get_input()
            self.rb_down.get_input()
        else:
             single_rb_input = get_yes_no_input("是否输入单个基极电阻 Rb？(y 或 N)(默认为N)")
             if single_rb_input == 'y':
                 rb_value = get_float_input("Rb(kOhm)(// 10 ^ 3) = ")
                 # 如果输入单个 Rb，假定它是与 Vcc 相连的上偏置电阻，下偏置电阻无穷大。
                 self.rb_up.values.append(rb_value)
                 # 下偏置电阻默认是并联，没有输入时等效无穷大，符合单个 Rb 接地的情况。
             else:
                 # 假定 Rb 无穷大 (例如基极直接连接到信号源，没有偏置电阻)
                 # 上下偏置电阻都为无穷大，符合没有偏置电阻的情况。
                 pass # Resistor 类的默认行为已经处理了没有输入的情况

        self.rc.get_input()
        self.re_dc.get_input()


    def calculate_dc_operating_point(self):
        """计算直流工作点。"""
        print("\n--- 计算直流工作点 ---")

        # 计算等效电阻
        rb_up_eq = self.rb_up.calculate_equivalent()
        rb_down_eq = self.rb_down.calculate_equivalent()
        rc_eq = self.rc.calculate_equivalent()
        re_dc_eq = self.re_dc.calculate_equivalent()

        # 计算基极电压 Vb
        # 对于分压偏置电路，Vb = Vcc * (Rb_down_eq / (Rb_up_eq + Rb_down_eq))
        # 如果只有单个 Rb 接 Vcc，下偏置电阻无穷大，Rb_down_eq / (Rb_up_eq + Rb_down_eq) 趋近于 1，Vb 趋近于 Vcc。
        # 如果 Rb 无穷大 (没有偏置电阻)，上下偏置电阻都无穷大，Rb_down_eq / (Rb_up_eq + Rb_down_eq) 无法确定。
        # 采用更通用的方法：根据基极回路方程计算 Ib，然后计算 Vb = Vcc - Ib * Rb_up_eq (如果 Rb_up_eq 有限) 或 Vb = Ib * Rb_down_eq (如果 Rb_down_eq 有限)
        # 或者直接使用戴维宁定理计算基极等效电压和电阻。

        # 使用戴维宁定理计算基极等效电压 Vbb 和等效电阻 Rbb
        # Vbb = Vcc * (Rb_down_eq / (Rb_up_eq + Rb_down_eq))
        # Rbb = Rb_up_eq 并联 Rb_down_eq

        if math.isinf(rb_up_eq) and math.isinf(rb_down_eq):
            # 没有偏置电阻，Vbb 和 Rbb 无法确定，或取决于信号源内阻。
            # 假定基极直接连接到信号源，没有偏置电阻。
            # 这种情况下，简单分析可能不适用，但根据原始代码逻辑，似乎假定了 Ib=0, Ic=0, Vce=Vcc
            # 在 OOP 版本中，我们尝试更通用的计算。
            # 如果 Rb 无穷大，基极电流 Ib 趋近于 0。
            self.ib = 0.0
            self.ie = 0.0
            self.ic = 0.0
            self.ve = self.ie * re_dc_eq # Ie = 0 导致 Ve = 0
            self.vb = self.ve + self.transistor.vbe # Vb = Vbe
            self.vce = self.vcc - self.ic * rc_eq - self.ie * re_dc_eq # Ic = 0, Ie = 0 导致 Vce = Vcc

            print("提示：基极等效电阻 Rb 为无穷大，假定 Ib=0, Ic=0, Ie=0, Vb=Vbe, Ve=0, Vce=Vcc。")

        elif (rb_up_eq + rb_down_eq) != 0.0:
             # 计算戴维宁等效电压 Vbb
             if math.isinf(rb_up_eq):
                 vbb = self.vcc # 上偏置开路，Vbb 接近 Vcc
             elif math.isinf(rb_down_eq):
                 vbb = 0.0 # 下偏置开路，Vbb 接近地
             else:
                 vbb = self.vcc * (rb_down_eq / (rb_up_eq + rb_down_eq))

             # 计算戴维宁等效电阻 Rbb
             if math.isinf(rb_up_eq):
                 rbb_eq = rb_down_eq
             elif math.isinf(rb_down_eq):
                 rbb_eq = rb_up_eq
             else:
                 rbb_eq = (rb_up_eq * rb_down_eq) / (rb_up_eq + rb_down_eq)

             # 根据基极回路方程计算基极电流 Ib
             # Vbb - Ib * Rbb - Vbe - Ie * Re_dc_eq = 0
             # Vbb - Ib * Rbb - Vbe - (1 + beta) * Ib * Re_dc_eq = 0
             # Ib * (Rbb + (1 + beta) * Re_dc_eq) = Vbb - Vbe
             # Ib = (Vbb - Vbe) / (Rbb + (1 + beta) * Re_dc_eq)

             denominator = rbb_eq + (1 + self.transistor.beta) * re_dc_eq
             if denominator != 0.0:
                 self.ib = (vbb - self.transistor.vbe) / denominator
                 if self.ib < 0:
                     self.ib = 0.0 # 基极电流不能为负，表示晶体管截止
                     print("警告：计算得到的基极电流为负，晶体管处于截止状态。")
             else:
                 self.ib = float('nan')
                 print("警告：计算基极电流时分母为零，Ib 无法确定。")

             # 计算其他直流参数
             if not math.isnan(self.ib):
                 self.ie = (1 + self.transistor.beta) * self.ib
                 self.ic = self.transistor.beta * self.ib
                 self.ve = self.ie * re_dc_eq
                 self.vb = self.ve + self.transistor.vbe
                 self.vce = self.vcc - self.ic * rc_eq - self.ie * re_dc_eq
             else:
                 self.ie = float('nan')
                 self.ic = float('nan')
                 self.ve = float('nan')
                 self.vb = float('nan')
                 self.vce = float('nan')

        else:
             # Rb_up_eq + Rb_down_eq == 0.0，即上下偏置电阻都为 0，基极直接短接到 Vcc 和地，电路不正常。
             self.ib = float('nan')
             self.ie = float('nan')
             self.ic = float('nan')
             self.ve = float('nan')
             self.vb = float('nan')
             self.vce = float('nan')
             print("警告：上下偏置电阻和为零，电路连接不正常，无法计算直流工作点。")


    def calculate_ac_characteristics(self):
        """计算交流特性。"""
        print("\n--- 计算交流特性 ---")

        # 询问是否需要计算交流特性
        ac_part = get_yes_no_input("是否需要计算交流特性（y 或 N）（默认为N）:")

        if ac_part == 'y':
            self.transistor.get_ac_parameters_input()
            self.transistor.calculate_rbe(self.ic)

            # 询问交流通路下发射极与公共接地之间是否有电阻
            re_ac_present = get_yes_no_input("在交流通路下发射极与公共接地之间是否有电阻？（y 或 N）（默认为N）")

            if re_ac_present == 'y':
                 self.re_ac.get_input()
                 re_ac_eq = self.re_ac.calculate_equivalent()
            else:
                 re_ac_eq = 0.0 # 交流通路下发射极直接接地

            # 计算交流负载电阻 RoSum (集电极电阻 Rc 与负载电阻 Rl 的并联)
            rc_eq = self.rc.calculate_equivalent()
            if not (math.isnan(rc_eq) or math.isnan(self.rl) or (math.isinf(rc_eq) and math.isinf(self.rl))):
                # 处理无穷大的并联
                if math.isinf(rc_eq):
                    self.ro_sum = self.rl
                elif math.isinf(self.rl):
                    self.ro_sum = rc_eq
                elif (rc_eq + self.rl) != 0.0:
                    self.ro_sum = (rc_eq * self.rl) / (rc_eq + self.rl)
                else:
                    self.ro_sum = float('nan') # 分母为零
                    print("警告：计算交流负载电阻时分母为零，RoSum 无法确定。")
            else:
                self.ro_sum = float('nan')
                print("警告：集电极电阻 Rc 或负载电阻 Rl 无效，RoSum 无法确定。")


            # 计算电压增益 Au
            # Au = - beta * RoSum / (rbe + (1 + beta) * Re_ac_eq)
            au_denominator = self.transistor.rbe + (1 + self.transistor.beta) * re_ac_eq
            if not math.isnan(self.ro_sum) and not math.isinf(au_denominator) and au_denominator != 0.0:
                self.au = -(self.transistor.beta * self.ro_sum) / au_denominator
            else:
                 self.au = float('nan') # 分母为零 或无穷大，或 RoSum 为 NaN


            # 计算输入电阻 Ri
            # Ri = Rb_eq 并联 (rbe + (1 + beta) * Re_ac_eq)
            # 交流通路下，Rb_up 和 Rb_down 并联作为等效基极电阻
            rb_up_eq_ac = self.rb_up.calculate_equivalent()
            rb_down_eq_ac = self.rb_down.calculate_equivalent()

            if not (math.isinf(rb_up_eq_ac) and math.isinf(rb_down_eq_ac)):
                 if math.isinf(rb_up_eq_ac):
                      rb_eq_ac = rb_down_eq_ac
                 elif math.isinf(rb_down_eq_ac):
                      rb_eq_ac = rb_up_eq_ac
                 elif (rb_up_eq_ac + rb_down_eq_ac) != 0.0:
                      rb_eq_ac = (rb_up_eq_ac * rb_down_eq_ac) / (rb_up_eq_ac + rb_down_eq_ac)
                 else:
                      rb_eq_ac = float('nan')
                      print("警告：计算交流基极等效电阻时分母为零，Ri 无法确定。")
            else:
                 rb_eq_ac = float('inf') # 上下偏置电阻都无穷大，等效基极电阻无穷大


            ri_parallel_term = self.transistor.rbe + (1 + self.transistor.beta) * re_ac_eq
            if not (math.isnan(rb_eq_ac) or math.isnan(ri_parallel_term) or (math.isinf(rb_eq_ac) and math.isinf(ri_parallel_term))):
                 # 处理无穷大的并联
                 if math.isinf(rb_eq_ac):
                     self.ri = ri_parallel_term
                 elif math.isinf(ri_parallel_term):
                     self.ri = rb_eq_ac
                 elif (rb_eq_ac + ri_parallel_term) != 0.0:
                     self.ri = (rb_eq_ac * ri_parallel_term) / (rb_eq_ac + ri_parallel_term)
                 else:
                     self.ri = float('nan') # 分母为零
            else:
                 self.ri = float('nan') # rb_eq_ac 或 ri_parallel_term 为 NaN


            # 计算输出电阻 Ro
            # Ro = RcValue_eq (不考虑晶体管输出电阻 ro)
            self.ro = rc_eq

        else:
            print("跳过交流特性计算。")


    def print_results(self):
        """输出计算结果。"""
        # 输出直流工作点结果
        print(f"\n直流工作点参数：")
        # 使用 isnan() 检查是否为 NaN，使用 isinf() 检查是否为 Infinity
        print(f"基极电压 Vb = {'NaN' if math.isnan(self.vb) else f'{self.vb:.4f} V'}")
        print(f"发射极电压 Ve = {'NaN' if math.isnan(self.ve) else f'{self.ve:.4f} V'}")
        print(f"集电极电流 Ic = {'NaN' if math.isnan(self.ic) else (f'{self.ic:.4f} mA' if not math.isinf(self.ic) else 'Infinity mA')}") # 假设电流单位是 mA (电阻单位 kOhm, 电压单位 V)
        print(f"基极电流 Ib = {'NaN' if math.isnan(self.ib) else (f'{self.ib:.4f} mA' if not math.isinf(self.ib) else 'Infinity mA')}")   # 假设电流单位是 mA
        print(f"发射极电流 Ie = {'NaN' if math.isnan(self.ie) else (f'{self.ie:.4f} mA' if not math.isinf(self.ie) else 'Infinity mA')}") # 假设电流单位是 mA
        print(f"集电极-发射极电压 Vce = {'NaN' if math.isnan(self.vce) else f'{self.vce:.4f} V'}")

        # 输出交流特性结果
        if not math.isnan(self.au): # 只有计算了交流特性才输出
             print("\n交流特性参数：")
             print(f"交流输入电阻 rbe = {'NaN' if math.isnan(self.transistor.rbe) else (f'{self.transistor.rbe:.4f} kOhm' if not math.isinf(self.transistor.rbe) else 'Infinity kOhm')}")
             # 判断 Au, Ri, Ro 是否是有效数字，避免输出 nan 或 inf
             print(f"电压增益 Au = {'NaN' if math.isnan(self.au) else (f'{self.au:.4f}' if not math.isinf(self.au) else ('Infinity' if self.au == float('inf') else '-Infinity'))}")
             print(f"输入电阻 Ri = {'NaN' if math.isnan(self.ri) else (f'{self.ri:.4f} kOhm' if not math.isinf(self.ri) else 'Infinity kOhm')}")
             print(f"输出电阻 Ro = {'NaN' if math.isnan(self.ro) else (f'{self.ro:.4f} kOhm' if not math.isinf(self.ro) else 'Infinity kOhm')}")


# 主程序入口
if __name__ == "__main__":
    circuit = CommonEmitterAmplifier()
    circuit.get_parameters_input()
    circuit.calculate_dc_operating_point()
    circuit.calculate_ac_characteristics()
    circuit.print_results()
    print("\n程序运行完毕。")