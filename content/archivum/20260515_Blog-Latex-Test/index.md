
## 1. 字体样式


$$
\mathbf{粗体数学} \quad \mathit{斜体数学} \quad \mathrm{罗马体} \quad \mathsf{无衬线体} \quad \mathtt{打字机体}
$$



$$
\mathcal{CALLIGRAPHIC} \quad \mathbb{BLACKBOARD} \quad \mathfrak{Fraktur}
$$



$$
\text{普通文本} \quad \textbf{粗体文本} \quad \textit{斜体文本} \quad \underline{下划线} \quad \overline{上划线}
$$


---

## 2. 字号大小


$$
{\tiny tiny} \;
{\scriptsize scriptsize} \;
{\footnotesize footnotesize} \;
{\small small} \;
{\normalsize normalsize} \;
{\large large} \;
{\Large Large} \;
{\LARGE LARGE} \;
{\huge huge} \;
{\Huge Huge}
$$


---

## 3. 颜色（需 \color 命令）


$$
\color{red}{红色} \;
\color{blue}{蓝色} \;
\color{green}{绿色} \;
\color{orange}{橙色} \;
\color{purple}{紫色} \;
\color{gray}{灰色}
$$



$$
\colorbox{yellow}{黄色背景} \quad
\colorbox{cyan}{青色背景} \quad
\colorbox{magenta}{品红背景}
$$


---

## 4. 空格与间距


$$
a \quad b \qquad c \;
d \: e \, f \! g \hspace{1cm} h
$$


---

## 5. 上下标与堆叠


$$
x^{2} \quad x^{abc} \quad x_{1} \quad x_{ij}^{kl}
$$



$$
\overset{上方}{=} \quad \underset{下方}{=} \quad \overset{上方}{\underset{下方}{=}}
$$



$$
\stackrel{\text{def}}{=} \quad \xrightarrow{\text{映射}} \quad \xleftarrow{\text{反向}}
$$


---

## 6. 分式与根式


$$
\frac{a}{b} \quad \frac{1}{1+\frac{1}{x}} \quad \tfrac{小分数}{小分母}
$$



$$
\sqrt{x} \quad \sqrt[3]{x} \quad \sqrt{\frac{a}{b}} \quad \sqrt[4]{\frac{x}{y}}
$$


---

## 7. 括号与定界符


$$
( \quad ) \quad [ \quad ] \quad \{ \quad \} \quad \langle \quad \rangle \quad \lceil \quad \rceil \quad \lfloor \quad \rfloor
$$



$$
\left( \frac{a}{b} \right) \quad
\left[ \frac{a}{b} \right] \quad
\left\{ \frac{a}{b} \right\} \quad
\left\langle \frac{a}{b} \right\rangle
$$



$$
\left. \frac{df}{dx} \right|_{x=0} \quad
\underbrace{a + b + c}_{\text{下方注释}} \quad
\overbrace{a + b + c}^{\text{上方注释}}
$$


---

## 8. 希腊字母


$$
\alpha \beta \gamma \delta \epsilon \varepsilon \zeta \eta \theta \vartheta \iota \kappa \lambda \mu \nu \xi o \pi \varpi \rho \varrho \sigma \varsigma \tau \upsilon \phi \varphi \chi \psi \omega
$$



$$
\Gamma \Delta \Theta \Lambda \Xi \Pi \Sigma \Upsilon \Phi \Psi \Omega
$$


---

## 9. 常用符号


$$
\pm \quad \mp \quad \times \quad \div \quad \cdot \quad \circ \quad \bullet \quad \ast \quad \star
$$



$$
\leq \quad \geq \quad \neq \quad \approx \quad \equiv \quad \sim \quad \simeq \quad \propto \quad \ll \quad \gg
$$



$$
\subset \quad \supset \quad \subseteq \quad \supseteq \quad \in \quad \notin \quad \ni \quad \emptyset \quad \varnothing
$$



$$
\forall \quad \exists \quad \nexists \quad \neg \quad \land \quad \lor \quad \implies \quad \iff \quad \top \quad \bot
$$



$$
\infty \quad \partial \quad \nabla \quad \Delta \quad \hbar \quad \ell \quad \wp \quad \Re \quad \Im \quad \aleph
$$


---

## 10. 箭头


$$
\leftarrow \quad \rightarrow \quad \leftrightarrow \quad \longleftarrow \quad \longrightarrow \quad \longleftrightarrow
$$



$$
\Leftarrow \quad \Rightarrow \quad \Leftrightarrow \quad \Longleftarrow \quad \Longrightarrow \quad \Longleftrightarrow
$$



$$
\uparrow \quad \downarrow \quad \updownarrow \quad \Uparrow \quad \Downarrow \quad \Updownarrow
$$



$$
\nearrow \quad \searrow \quad \swarrow \quad \nwarrow \quad \mapsto \quad \longmapsto \quad \rightleftharpoons
$$


---

## 11. 大型运算符


$$
\sum_{i=1}^{n} i^2 \qquad \prod_{k=1}^{n} k \qquad \coprod_{i \in I} X_i
$$



$$
\int_{a}^{b} f(x) \, dx \qquad \iint_D f(x,y) \, dx\,dy \qquad \iiint_V f(x,y,z) \, dx\,dy\,dz
$$



$$
\oint_C \vec{F} \cdot d\vec{r} \qquad \bigcap_{i=1}^{n} A_i \qquad \bigcup_{i=1}^{n} A_i \qquad \bigvee \bigwedge
$$


---

## 12. 矩阵与行列式


$$
\begin{pmatrix}
a_{11} & a_{12} & a_{13} \\
a_{21} & a_{22} & a_{23} \\
a_{31} & a_{32} & a_{33}
\end{pmatrix}
$$



$$
\begin{bmatrix}
a & b \\
c & d
\end{bmatrix}
\quad
\begin{vmatrix}
a & b \\
c & d
\end{vmatrix}
\quad
\begin{Vmatrix}
a & b \\
c & d
\end{Vmatrix}
$$



$$
\begin{Bmatrix}
x \\ y
\end{Bmatrix}
\quad
\begin{smallmatrix}
a & b \\
c & d
\end{smallmatrix}
$$


---

## 13. 多行公式对齐


$$
\begin{aligned}
f(x) &= (a + b)^2 \\
     &= a^2 + 2ab + b^2
\end{aligned}
$$



$$
\begin{cases}
x + y = 5 \\
2x - 3y = -4
\end{cases}
$$



$$
\begin{array}{c|c}
\text{列1} & \text{列2} \\
\hline
a & b \\
c & d
\end{array}
$$


---

## 14. 特殊装饰


$$
\hat{a} \quad \widehat{abc} \quad \bar{x} \quad \overline{xyz} \quad \vec{v} \quad \overrightarrow{AB} \quad \overleftarrow{BA}
$$



$$
\dot{x} \quad \ddot{x} \quad \dddot{x} \quad \tilde{x} \quad \widetilde{xyz}
$$



$$
\acute{a} \quad \grave{a} \quad \breve{a} \quad \check{a} \quad \mathring{a}
$$


---

## 15. 框与注释


$$
\boxed{E = mc^2} \quad \fbox{文本} \quad \xcancel{删除} \quad \cancel{取消}
$$



$$
\underbrace{a + b + c}_{\text{和}} \qquad \overbrace{a \cdot b \cdot c}^{\text{积}}
$$


---

## 16. 定理类环境（用 amsthm 模拟）


$$
\textbf{定理 1.} \quad \text{设 } a, b \in \mathbb{R}, \text{ 则 } (a+b)^2 = a^2 + 2ab + b^2.
$$



$$
\textit{证明：} \quad \text{展开即可得证。} \quad \blacksquare
$$


---

## 17. 化学式（用 mhchem 模拟）


$$
\ce{H2O} \quad \ce{CO2} \quad \ce{^{235}_{92}U} \quad \ce{CH3COOH}
$$



$$
\ce{A ->[催化剂] B} \quad \ce{A <=> B} \quad \ce{A + B -> C}
$$


---

## 18. 综合复杂示例


$$
\boxed{
\begin{aligned}
\mathcal{F}(\xi) &= \int_{-\infty}^{\infty} f(x) \, e^{-2\pi i x \xi} \, dx \\
\widehat{f}(\omega) &= \frac{1}{\sqrt{2\pi}} \int_{-\infty}^{\infty} f(t) \, e^{-i\omega t} \, dt
\end{aligned}
}
$$



$$
\begin{vmatrix}
\color{red}{\lambda - a_{11}} & -a_{12} & \cdots & -a_{1n} \\
-a_{21} & \color{blue}{\lambda - a_{22}} & \cdots & -a_{2n} \\
\vdots & \vdots & \ddots & \vdots \\
-a_{n1} & -a_{n2} & \cdots & \color{green}{\lambda - a_{nn}}
\end{vmatrix}
= 0
$$

