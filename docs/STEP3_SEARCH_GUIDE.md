# Step 3: Web and Deep Search for Resources

## Assignment Requirement
Build a knowledge corpus through systematic search, **NOT by generating content**. The RAG system must be grounded in real external sources.

---

## 🔍 Search Strategy

### 1. Naive Search (Start Here)
Use standard search engines to find quality sources:
- **Google Scholar**: Academic papers on structural breaks, forecasting
- **Google**: Blog posts, tutorials, case studies
- **Perplexity**: AI-assisted search for synthesized overviews
- **Bing Academic**: Alternative academic search
- **arXiv.org**: Preprints on time series, econometrics

### 2. Deep Search Frameworks (Optional/Advanced)
For more systematic retrieval:
- **ManuSearch** [Huang et al., 2025]: Manual-assisted deep search
- **Open Deep Search (ODS)** [Alzubi et al., 2025]: Open-source deep search
- **R-Search** [Zhao et al., 2025]: Research-focused search

---

## 📚 Source Collection Goals

### Minimum Requirements
- **10-15 quality sources** minimum
- **Diverse types**: Papers, reports, blogs, videos, podcasts
- **Documented metadata**: Title, URL, Type, Relevance

### Recommended Mix
1. **Academic Papers** (4-6 sources)
   - Focus: Structural break detection, regime-switching models, nowcasting
   - Where: Google Scholar, arXiv, SSRN, NBER

2. **Technical Reports** (2-3 sources)
   - Focus: Central bank reports, IMF/World Bank documents, risk management
   - Where: Federal Reserve, ECB, BIS websites

3. **Tutorials/Blogs** (2-3 sources)
   - Focus: Practical implementation, Python code examples
   - Where: Towards Data Science, Analytics Vidhya, company blogs

4. **Books/Chapters** (1-2 sources)
   - Focus: Time series analysis, econometrics textbooks
   - Where: SpringerLink, JSTOR (if accessible)

5. **Multimedia** (1-2 sources, optional)
   - Focus: Video lectures, podcasts on forecasting
   - Where: YouTube (university channels), Coursera

---

## 🔑 Search Keywords

### Core Topics
- "structural breaks time series"
- "regime switching models"
- "break detection methods"
- "Chow test" OR "CUSUM test" OR "Bai-Perron"
- "nowcasting macroeconomic indicators"
- "forecasting under uncertainty"

### Domain-Specific
- "corporate forecasting structural change"
- "financial time series regime change"
- "economic shock detection"
- "adaptive forecasting methods"

### Methodological
- "Markov-switching models"
- "threshold autoregression"
- "Bayesian model averaging forecasting"
- "rolling window estimation"

---

## 📋 Documentation Template

For each source, record in `docs/sources.csv`:

| Field | Description | Example |
|-------|-------------|---------|
| **Title** | Full title of source | "The Great Crash, the Oil Price Shock, and the Unit Root Hypothesis" |
| **URL** | Direct link | https://doi.org/10.2307/1913712 |
| **Type** | Academic Paper / Report / Blog / Video / Book Chapter | Academic Paper |
| **Relevance** | Core / Advanced / Reference / Case Study | Core |

---

## 🎯 Example Search Workflow

### Step 1: Academic Foundation (Google Scholar)
```
Search: "structural breaks forecasting"
Filter: Since 2010
Sort: Cited by

Target: Find 3-5 highly-cited foundational papers
```

### Step 2: Practical Methods (Google)
```
Search: "detecting structural breaks python"
Filter: Past 3 years
Look for: Tutorials, code examples, blog posts

Target: Find 2-3 implementation guides
```

### Step 3: Domain Context (Institutional Sites)
```
Sites: federalreserve.gov, imf.org, ecb.europa.eu
Search within site: "forecasting breaks" OR "regime change"

Target: Find 2-3 policy/technical reports
```

### Step 4: Case Studies (Industry)
```
Search: "forecasting COVID-19 structural break"
         "pandemic nowcasting"
Look for: Real-world applications, case studies

Target: Find 1-2 applied examples
```

---

## ✅ Quality Checklist

For each source, verify:
- [ ] **Authoritative**: Published by credible author/institution
- [ ] **Relevant**: Directly addresses forecasting/structural breaks
- [ ] **Accessible**: Can be downloaded/viewed (check paywalls)
- [ ] **Usable**: Contains substantive content (not just abstract)
- [ ] **Diverse**: Covers different aspects (theory, methods, applications)

---

## 📥 Download & Organize

### 1. Create Local Copies
```bash
cd plp/data/

# For papers (PDF)
# Download and save as: AuthorYear_ShortTitle.pdf
# Example: Perron1989_GreatCrash.pdf

# For web content (HTML/text)
# Save as markdown: Topic_Source_Date.md
# Example: NowcastingCOVID_FedReserve_2020.md
```

### 2. Extract Text
- **PDFs**: Use tools like `pypdf`, `pdfplumber`, or manual copy-paste
- **Web pages**: Save as markdown or use web scraping tools
- **Videos**: Extract transcripts (YouTube auto-captions, etc.)

### 3. Document Metadata
Update `docs/sources.csv` as you go:
```csv
Title,URL,Type,Relevance
"The Great Crash, the Oil Price Shock, and the Unit Root Hypothesis",https://doi.org/10.2307/1913712,Academic Paper,Core
"Nowcasting in a Pandemic Using Non-traditional Data",https://www.federalreserve.gov/...,Report,Advanced
...
```

---

## 🚫 What NOT to Do

❌ **Don't generate fake content** (we had placeholder docs initially)
❌ **Don't rely only on ChatGPT/LLM summaries** (need original sources)
❌ **Don't skip documentation** (must track all sources)
❌ **Don't use low-quality sources** (random blogs, Wikipedia only)
❌ **Don't ignore licensing** (respect copyright, paywalls)

---

## 🔄 After Collection

Once you have 10-15 sources:

1. **Place files in `data/`**
   ```bash
   data/
   ├── Perron1989_GreatCrash.pdf
   ├── Hamilton1989_RegimeSwitching.pdf
   ├── BaiPerron2003_MultipleBreaks.pdf
   ├── FedNowcasting2020.md
   └── ...
   ```

2. **Update `docs/sources.csv`** with all metadata

3. **Re-run ingestion**
   ```bash
   make ingest
   ```

4. **Test retrieval** on real queries

5. **Evaluate** with `make eval-basic` and `make eval-judge`

---

## 📖 Recommended Starting Sources

### Must-Read Papers (Search for these)
1. Perron, P. (1989). "The Great Crash, the Oil Price Shock, and the Unit Root Hypothesis"
2. Bai, J., & Perron, P. (2003). "Computation and Analysis of Multiple Structural Change Models"
3. Hamilton, J. D. (1989). "A New Approach to the Economic Analysis of Nonstationary Time Series"
4. Giannone, D., Reichlin, L., & Small, D. (2008). "Nowcasting: The Real-Time Informational Content of Macroeconomic Data"

### Institutional Resources
1. Federal Reserve: Search "Economic Forecasting" section
2. IMF Working Papers: Search "structural breaks"
3. BIS Papers: Search "forecasting uncertainty"

### Tutorials (Search for these)
1. "Structural Break Detection in Python" (various blogs)
2. "Regime-Switching Models Tutorial" (quantitative finance sites)

---

## 🎓 Assignment Alignment

**Step 3** requires:
- ✅ Systematic search (naive + optional deep search)
- ✅ 10-15 quality sources
- ✅ Documented metadata (title, URL, type, relevance)
- ✅ Diverse source types
- ✅ Real external content (not generated)

**Update to README**: Note that the current 3 `.md` files are **placeholder stubs** and should be replaced with actual sources per Step 3.

---

## ⏭️ Next Actions for You

1. **Start naive search** using keywords above
2. **Download/save 10-15 sources** to `data/`
3. **Fill out `docs/sources.csv`** as you go
4. **Replace placeholder files** (structural_breaks.md, etc.) with real content
5. **Re-run `make ingest`** to rebuild FAISS index
6. **Test & evaluate** with real corpus

---

**Note**: The current `data/*.md` files are generated placeholders for testing the system. You must replace them with real sources to complete Step 3 properly.
