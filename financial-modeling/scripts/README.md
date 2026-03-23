# Financial Services Scripts

配套 Python 脚本模板，支持 11 个金融分析 Skills。

## 安装依赖

```bash
pip install requests openpyxl python-pptx rich
```

## 脚本列表

| 脚本 | 功能 | 对应 Skill |
|------|------|-----------|
| `fetch_data.py` | 获取股票实时数据 (Yahoo/Tencent) | 通用 |
| `create_3statement_model.py` | 生成三表财务模型 Excel 模板 | financial-modeling |
| `dcf_calculator.py` | DCF 估值计算 | dcf-modeling |
| `comps_calculator.py` | 可比公司估值分析 | comparables-analysis |
| `profile_generator.py` | 生成公司概况 HTML | strip-profile |
| `qc_checker.py` | PPT 质量检查 | presentation-qc |

## 使用示例

### 1. 获取股票数据

```bash
# US stock
python3 fetch_data.py AAPL

# A-share
python3 fetch_data.py sh600519

# HK stock
python3 fetch_data.py hk00700
```

### 2. 创建三表财务模型

```bash
python3 create_3statement_model.py Company_Model.xlsx
```

生成包含以下工作表的 Excel 文件：
- **Assumptions**: 关键假设（蓝色输入单元格）
- **Income Statement**: 利润表
- **Balance Sheet**: 资产负债表
- **Cash Flow**: 现金流量表

### 3. DCF 估值计算

```bash
python3 dcf_calculator.py --example
```

输出示例：
```
DCF VALUATION RESULTS
============================================================
Projections:
  Year 1: Revenue $1,000.00M, FCFF $87.50M
  Year 2: Revenue $1,120.00M, FCFF $98.00M
  ...
Valuation Summary:
  PV of Explicit Period: $350.12M
  Terminal Value: $1,500.00M
  Enterprise Value: $1,280.45M
  Value Per Share: $10.80
```

### 4. 可比公司分析

```bash
python3 comps_calculator.py --example
```

输出：
- 同行公司估值倍数对比表
- 倍数统计（Min/Max/Median/Mean）
- 目标公司隐含估值范围

### 5. 生成公司概况

```bash
python3 profile_generator.py --example
```

生成 `company_profile.html` - 可用于：
- Buyer lists
- Pitch books
- Teaser documents

### 6. PPT 质量检查

```bash
python3 qc_checker.py Client_Pitch.pptx
```

检查项目：
- 🔴 Critical: 占位符文本未替换
- 🟡 Important: 字体不一致、空幻灯片
- 🟢 Minor: 页码缺失、小数位数不一致

## 在代码中使用

```python
from dcf_calculator import DCFInputs, dcf_valuation
from comps_calculator import Company, analyze_comps
from profile_generator import CompanyProfile, generate_profile_html

# DCF example
inputs = DCFInputs(
    revenue=1_000_000_000,
    growth_rates=[0.15, 0.12, 0.10, 0.08, 0.06],
    ebitda_margin=0.25,
    depreciation_pct=0.05,
    capex_pct=0.07,
    nwc_pct=0.02,
    tax_rate=0.21,
    wacc=0.10,
    terminal_growth=0.03,
    net_debt=200_000_000,
    shares_outstanding=100_000_000
)
result = dcf_valuation(inputs)
print(f"Value per share: ${result['value_per_share']:.2f}")
```

## 数据源

| 市场 | 数据源 | 代码示例 |
|------|--------|---------|
| US Stocks | Yahoo Finance | `AAPL`, `MSFT` |
| China A-Shares | Tencent Finance | `sh600519`, `sz000001` |
| Hong Kong | Tencent Finance | `hk00700`, `hk09988` |

## 扩展开发

### 添加新的数据获取脚本

参考 `fetch_data.py` 的结构，为特定数据源创建新脚本：

```python
def fetch_source_name(symbol):
    url = f"https://api.example.com/{symbol}"
    resp = requests.get(url)
    return parse_response(resp)
```

### 添加新的计算模块

参考 `dcf_calculator.py` 使用 dataclass 定义输入，返回字典结果。

## 注意事项

1. **API 限制**: Yahoo Finance 有速率限制，大量请求请添加延迟
2. **数据准确性**: 脚本提供计算框架，关键数据请核对原始来源
3. **公式链接**: Excel 模板使用公式链接，修改假设会自动更新

## License

MIT License - 可自由使用和修改
