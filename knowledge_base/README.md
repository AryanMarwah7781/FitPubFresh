# Fitness Knowledge Base for LightRAG

Research papers and guidelines for building the fitness AI knowledge graph.

## Overview

This directory contains curated research papers and guidelines that will be processed by LightRAG to create a knowledge graph for the AI fitness coach.

## Structure

```
knowledge_base/
├── research_papers/
│   ├── strength_training/    # 20 papers
│   ├── hypertrophy/          # 15 papers
│   ├── nutrition/            # 10 papers
│   ├── recovery/             # 5 papers
│   └── exercise_science/     # 10 papers
├── guidelines/
│   ├── acsm_guidelines.pdf
│   ├── nsca_essentials.pdf
│   ├── cdc_physical_activity.pdf
│   └── who_recommendations.pdf
└── processed/
    ├── graph.json           # Knowledge graph (generated)
    ├── entities.json        # Extracted entities (generated)
    └── relations.json       # Entity relationships (generated)
```

## Target: 60+ Documents

### Research Papers (50+ papers)

#### Strength Training (20 papers)
- Progressive overload studies
- Frequency and volume research
- Periodization models
- Strength adaptations

**Key Papers to Find:**
1. Schoenfeld et al. - "Dose-response between resistance training volume and muscle hypertrophy"
2. Helms et al. - "Recommendations for natural bodybuilding contest preparation"
3. Krieger - "Single vs multiple sets of resistance exercise"
4. Gonzalez-Badillo et al. - "Moderate resistance training volume"
5. Rhea et al. - "A meta-analysis to determine the dose response for strength development"

#### Hypertrophy (15 papers)
- Muscle growth mechanisms
- Volume landmarks
- Rep ranges
- Time under tension
- Rest periods

**Key Papers:**
1. Schoenfeld et al. (2017) - "Resistance training volume"
2. Schoenfeld et al. (2016) - "Effects of resistance training frequency"
3. Schoenfeld et al. (2015) - "Effects of different volume-equated resistance training"
4. Brad ton et al. - "Effect of load on muscle activation"
5. Burd et al. - "Low-load high volume vs high-load low volume"

#### Nutrition (10 papers)
- Protein synthesis studies
- Macro distribution research
- Nutrient timing
- Energy balance

**Key Papers:**
1. Morton et al. (2018) - "Protein intake meta-analysis"
2. Schoenfeld et al. - "How much protein can the body use in a single meal"
3. Aragon et al. - "International society of sports nutrition position stand: diets and body composition"
4. Phillips & Van Loon - "Dietary protein for athletes"
5. Helms et al. - "Evidence-based recommendations for contest prep nutrition"

#### Recovery (5 papers)
- Sleep and performance
- Deload protocols
- Overtraining syndrome
- Active recovery

**Key Papers:**
1. Halson - "Sleep in elite athletes"
2. Kellmann et al. - "Recovery and Performance in Sport"
3. Tavares et al. - "Effects of growth hormone administration on muscle strength"

#### Exercise Science Fundamentals (10 papers)
- Biomechanics
- Motor learning
- Fatigue mechanisms
- Adaptation theory

### Guidelines (5+ documents)

#### Must-Have Guidelines:
1. **ACSM (American College of Sports Medicine)**
   - Position Stand on Progressive Models in Resistance Training
   - Guidelines for Exercise Testing and Prescription

2. **NSCA (National Strength and Conditioning Association)**
   - Essentials of Strength Training and Conditioning
   - Position Statement on Training Frequency

3. **CDC (Centers for Disease Control)**
   - Physical Activity Guidelines for Americans
   - Strength Training Guidelines

4. **WHO (World Health Organization)**
   - Global Recommendations on Physical Activity for Health

5. **Evidence-Based Practice**
   - Systematic reviews and meta-analyses
   - Clinical practice guidelines

## How to Collect Papers

### Method 1: PubMed (FREE)
```bash
# Visit: https://pubmed.ncbi.nlm.nih.gov/

# Search queries:
- "resistance training volume hypertrophy"
- "protein synthesis muscle"
- "strength training frequency"
- "progressive overload adaptations"
- "deload recovery"

# Filter:
- Free full text
- Published in last 10 years
- Meta-analysis or randomized controlled trial
```

### Method 2: Google Scholar (FREE)
```bash
# Visit: https://scholar.google.com/

# Search with author names:
- "Schoenfeld resistance training"
- "Helms bodybuilding"
- "Morton protein"
- "Krieger meta-analysis"

# Download PDFs from free sources
```

### Method 3: ResearchGate (FREE with account)
```bash
# Visit: https://www.researchgate.net/

# Create free account
# Request full-text from authors
# Many papers available for free download
```

### Method 4: University Repositories (FREE)
```bash
# Many universities have open-access repositories
# Search: "university repository exercise science"
```

## Naming Convention

Use descriptive names for easy identification:

```
# Format: FirstAuthor_Year_Topic.pdf
Examples:
- Schoenfeld_2017_Volume_Hypertrophy.pdf
- Morton_2018_Protein_Meta_Analysis.pdf
- Helms_2014_Contest_Prep_Nutrition.pdf
- ACSM_2009_Progressive_Resistance.pdf
```

## Processing with LightRAG (Day 3-4)

Once papers are collected, LightRAG will:

1. **Extract Text** from PDFs
2. **Chunk Documents** (512 tokens, 50 overlap)
3. **Extract Entities**:
   - Concepts: "Progressive Overload", "Hypertrophy"
   - Exercises: "Squat", "Bench Press"
   - Metrics: "Volume", "Frequency", "Intensity"
   - Studies: Author names and years

4. **Extract Relationships**:
   - "Progressive Overload" --required_for--> "Muscle Growth"
   - "Volume" --measured_in--> "Sets per Week"
   - "10-20 sets" --optimal_for--> "Hypertrophy"
   - "Schoenfeld 2017" --supports--> "Volume-Hypertrophy Relationship"

5. **Build Knowledge Graph**:
   - ~1,000 entities
   - ~5,000 relationships
   - Citation tracking
   - Multi-hop reasoning paths

## Quality Checklist

Before processing, ensure papers meet these criteria:

- ✅ Peer-reviewed publication
- ✅ Relevant to fitness coaching
- ✅ Evidence-based (not opinion pieces)
- ✅ Full text available (not just abstract)
- ✅ PDF format
- ✅ Readable text (not scanned images without OCR)

## Usage

After collecting papers:

```bash
# Process papers with LightRAG (Day 3)
cd services/lightrag
python3 process_papers.py

# This will:
# 1. Extract text from all PDFs
# 2. Build knowledge graph
# 3. Save to knowledge_base/processed/
# 4. Index for fast retrieval
```

## Cost

- **Paper Collection**: FREE (all sources mentioned are free)
- **Storage**: <500MB for 60 PDFs
- **LightRAG Processing**: ~$5-8 (Claude API for entity extraction)

## Timeline

- **Day 3 Morning**: Collect 60 papers (3-4 hours)
- **Day 3 Afternoon**: Setup LightRAG and process papers (3-4 hours)
- **Day 4**: Test retrieval quality and optimize

## Tips

1. **Start with meta-analyses and systematic reviews** - They cite many other studies
2. **Follow citations** - If you find a good paper, check its references
3. **Use review papers** - They summarize lots of research
4. **Prioritize recent papers** - Last 5-10 years for current evidence
5. **Verify author credibility** - Look for established researchers

## Next Steps

1. [ ] Collect 20 strength training papers
2. [ ] Collect 15 hypertrophy papers
3. [ ] Collect 10 nutrition papers
4. [ ] Collect 5 recovery papers
5. [ ] Download 5 official guidelines
6. [ ] Organize into subdirectories
7. [ ] Run LightRAG processing
8. [ ] Test knowledge graph retrieval

---

**Ready for Day 3!** 📚

Start collecting papers and we'll process them into a knowledge graph for the AI fitness coach.
