# create-involute-gear-in-Blender
Blenderで好きなインボリュート平歯車を作成するpythonファイル  
ラック歯先の丸みの指定は、JIS B 4350より0.4<m≤1でのみ行えるようにしました。
## example
- 名前"involute_gear", モジュール1mm, 歯幅10mm, 圧力角20°, 歯数40, 転移係数0, 細かさ10の歯車を作成する。  
create()

- 名前"aaa", モジュール1.5mm, 歯幅20mm, 圧力角14.5°, 歯数14, 限界転移係数, 細かさ15の歯車を作成する。   
create(name="aaa", m=1.5, b=20, alpha_deg=14.5, z=14, x_csw=True, t_len = 15)

- 名前"involute_gear", モジュール0.6mm, 歯幅10mm, 圧力角20°, 歯数40, 転移係数0, 細かさ10, ラック歯先の丸み無しの歯車を作成する。  
create(m=0.6)

- 名前"involute_gear", モジュール0.6mm, 歯幅10mm, 圧力角20°, 歯数40, 転移係数0, 細かさ10, ラック歯先の丸みありの歯車を作成する。  
create(m=0.6, rho_sw=True)
