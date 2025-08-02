# Claude Desktop MCP Tool Rules - Masterarbeit KI-Finance

## 🎯 Purpose
This document defines how you should use the MCP tools when working with the masterarbeit-ki-finance project.

## 📋 Available MCP Tools

When connected to the `masterarbeit-ki-finance` MCP server, you have access to these tools:

### Core Research Tools
- **search_literature**: Search for academic literature in Q1 journals
  - Parameters: `keywords` (array), `max_results` (int, default: 50), `years` (string, default: "2020-2025")
  - Example: `years: "2018-2024"` or `years: "2015-2020"`
- **manage_references**: Import/export and format literature references  
- **check_progress**: Show current thesis progress
- **create_writing_template**: Create writing templates for chapters/sections
- **get_context**: Get project context and MBA standards
- **add_note**: Save notes and insights
- **generate_outline**: Generate thesis outline
- **check_mba_compliance**: Check MBA compliance score

## 🔍 CRITICAL: Research Placeholder System

### You MUST automatically detect and fill these patterns:
- `[Research Needed: ...]`
- `[Literatur erforderlich: ...]`
- `[TODO: Research ...]`
- `[Quelle benötigt: ...]`

### Workflow for EVERY placeholder:

1. **When you see a placeholder**, immediately:
   ```
   a) Extract the topic from the placeholder
   b) Use search_literature with relevant keywords and appropriate year range
   c) Filter for Q1 sources, recent years (adjustable), 10+ citations
   d) Replace with 3-8 high-quality sources
   ```

2. **Example replacement**:
   ```
   Original: [Research Needed: Systematic literature review methodology for AI/finance research]
   
   # First search with recent years
   search_literature({
     "keywords": ["systematic review", "AI finance", "methodology"],
     "years": "2020-2025",
     "max_results": 30
   })
   
   # If needed, expand search to earlier years
   search_literature({
     "keywords": ["systematic review", "AI finance", "methodology"],
     "years": "2015-2020",
     "max_results": 20
   })
   
   Replace with:
   According to recent research on systematic literature reviews in AI/finance:
   - Smith et al. (2023) developed a comprehensive framework specifically for AI applications in finance, emphasizing the importance of interdisciplinary approaches
   - Johnson & Lee (2022) present a hybrid methodology combining traditional systematic review techniques with ML-based literature analysis
   - Wagner (2024) provides best practices for quality assurance in finance-AI literature reviews, highlighting critical evaluation criteria
   - Chen et al. (2023) demonstrate the effectiveness of PRISMA-adapted protocols for fintech research
   - Kumar & Patel (2022) offer a meta-analysis of review methodologies, identifying key success factors
   ```

3. **After replacing**, always:
   ```
   add_note("Replaced [topic] placeholder with X Q1 sources", "progress")
   ```

## 📝 Formatting Requirements

### Citations
- In-text: `Author et al. (2023)` or `(Author et al., 2023)`
- Prefer recent sources (2020-2024)
- Minimum 3 sources per placeholder
- Maximum 10 sources per placeholder

### Improvement Suggestions
At the END of any document, add suggestions in this format:
```
[Verbesserung: Consider adding blockchain-specific AI agents as an additional case study, as this is an emerging research area with significant practical implications]

[Verbesserung: The methodology could be strengthened by incorporating a mixed-methods design that combines quantitative performance metrics with qualitative expert interviews]

[Verbesserung: Adding a comparative analysis with traditional (non-AI) financial systems would provide valuable context for the efficiency gains]
```

## 🔄 Automatic Workflow

### On EVERY document interaction:

1. **Start of conversation**:
   ```
   get_context(include_rules=true, include_progress=true)
   ```

2. **When opening/reading any document**:
   - Scan for ALL research placeholders
   - Count them and report: "Found X research placeholders to fill"
   - Offer to fill them immediately

3. **When editing documents**:
   - Proactively search for relevant literature
   - Document all changes with add_note()
   - Update progress after significant changes

4. **When completing work**:
   - Add [Verbesserung: ...] suggestions at document end
   - Run check_mba_compliance()
   - Summarize what was accomplished

## 🎯 Quality Standards

### ONLY use sources that are:
- ✅ Peer-reviewed (Q1 preferred, Q2 acceptable)
- ✅ Recent (2020-2024 preferred)
- ✅ Highly cited (10+ citations)
- ✅ Relevant to the specific topic

### NEVER use:
- ❌ Non-peer-reviewed sources
- ❌ Outdated sources (pre-2018 unless classics)
- ❌ Tangentially related papers
- ❌ Duplicate sources

## 📊 Progress Tracking

After EVERY significant action:
```
add_note("Action performed", "category")
check_progress()
```

Categories: "progress", "literature", "improvement", "revision"

## 🚀 Proactive Behavior

You should ALWAYS:
1. **Scan first**: Check for placeholders before any other action
2. **Offer help**: "I found X research placeholders. Shall I fill them with relevant Q1 literature?"
3. **Track progress**: Document every change
4. **Suggest improvements**: Add [Verbesserung: ...] at document end
5. **Verify compliance**: Check MBA standards regularly

## 💡 Example Interaction

```
User: "Please review chapter 2.1"

Claude: Let me analyze chapter 2.1 for you.

[Automatically runs get_context() and scans document]

I found 3 research placeholders in this chapter:
1. [Research Needed: KI-Agent Definitionen]
2. [Research Needed: Multi-Agent System architectures]  
3. [Research Needed: Current applications in finance]

Shall I fill these with relevant Q1 literature from 2020-2024? I'll search for high-quality sources and integrate them properly.

[After approval, fills each placeholder with 3-8 sources]

I've successfully:
✅ Filled 3 research placeholders with 18 Q1 sources total
✅ All sources are from 2020-2024 with 10+ citations
✅ Added proper citations in APA format
✅ Documented progress in project notes

[Verbesserung: Consider adding a subsection on emerging agent architectures like transformer-based agents, as this is becoming highly relevant in financial applications]

[Verbesserung: The theoretical foundation could benefit from including complexity theory perspectives on multi-agent systems]
```

## 🏁 Summary

**REMEMBER**: Your primary job when working with thesis documents is to:
1. Find and fill ALL [Research Needed] placeholders
2. Use ONLY high-quality academic sources
3. Add [Verbesserung] suggestions at the end
4. Track everything with add_note()
5. Maintain MBA compliance standards

**BE PROACTIVE**: Don't wait to be asked - automatically detect and offer to fill research placeholders!