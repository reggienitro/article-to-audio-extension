# Article-to-Audio Project Priority Graph

## 🔥 **HIGH PRIORITY** (Immediate Impact)
```
┌─────────────────────────────────────────────────────────────┐
│ 1. Audio sequence ordering issues on iPhone                │ ★★★★★
│    └─ Affects daily usage, debugging needed               │
│                                                             │
│ 2. Add more voice options (6 → 15+ voices)                │ ★★★★☆
│    └─ Simple config change, immediate benefit             │
│                                                             │
│ 3. Refine deduplication algorithm                         │ ★★★☆☆
│    └─ Prevents text truncation, improves quality          │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 **MEDIUM PRIORITY** (Core Improvements)
```
┌─────────────────────────────────────────────────────────────┐
│ 4. Voice preference management in UI                       │ ★★★☆☆
│    └─ Save favorites, categorization                      │
│                                                             │
│ 5. Pocket/Instapaper API integration                      │ ★★★☆☆
│    └─ Reading list automation                             │
│                                                             │
│ 6. Washington Post/WSJ extractors                         │ ★★☆☆☆
│    └─ Expand paywall bypass beyond NYT                   │
│                                                             │
│ 7. Progress indicators during conversion                   │ ★★☆☆☆
│    └─ Better UX feedback                                  │
│                                                             │
│ 8. Better error messages in extension                     │ ★★☆☆☆
│    └─ User-friendly error handling                        │
│                                                             │
│ 9. Test Ollama TTS capabilities                          │ ★☆☆☆☆
│    └─ Alternative voice generation                        │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 **FUTURE FEATURES** (Roadmap)
```
┌─────────────────────────────────────────────────────────────┐
│ 10. Batch URL conversion to web UI                        │ ★★☆☆☆
│     └─ Process multiple articles                          │
│                                                             │
│ 11. Cross-device sync configuration UI                    │ ★☆☆☆☆
│     └─ Cloud provider settings                            │
│                                                             │
│ 12. Credential storage system                             │ ★★★☆☆
│     └─ Auto-login for subscription sites                  │
│                                                             │
│ 13. Native mobile app                                     │ ★☆☆☆☆
│     └─ iOS/Android apps                                   │
│                                                             │
│ 14. Podcast-style features                                │ ★☆☆☆☆
│     └─ RSS feeds, metadata                                │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 **INTEGRATION & INFRASTRUCTURE**
```
┌─────────────────────────────────────────────────────────────┐
│ 15. TaskMaster integration                                 │ ★☆☆☆☆
│     └─ Project management                                  │
│                                                             │
│ 16. Supabase integration (User backlogged)                │ ★☆☆☆☆
│     └─ Cloud backend                                       │
│                                                             │
│ 17. CI/CD pipeline setup                                  │ ★☆☆☆☆
│     └─ Automated testing/deployment                        │
└─────────────────────────────────────────────────────────────┘
```

## 📊 **Priority Matrix**

```
High Impact │ 1. Audio ordering     │ 2. Voice expansion
           │ 3. Deduplication      │ 12. Credentials
           │                       │
───────────┼───────────────────────┼─────────────────────
Low Impact │ 5. Reading lists      │ 11. Sync config
           │ 7. Progress UI        │ 13. Native apps
           │ 9. Ollama TTS         │ 14. Podcast features
           │                       │
           │ Quick Win            │ Major Project
```

## 🚀 **Recommended Next Actions**

### **Week 1-2: Quick Wins**
1. **Voice expansion** (2-3 hours)
   - Simple config file update
   - Immediate user benefit

2. **Audio ordering debug** (4-6 hours)
   - Use transcript analysis
   - Fix iPhone playback sequence

### **Week 3-4: Quality Improvements**
3. **Deduplication refinement** (6-8 hours)
   - Fix sentence boundary detection
   - Prevent text truncation

4. **Voice preference UI** (8-10 hours)
   - Save user favorites
   - Voice categorization

### **Month 2: Major Features**
5. **Pocket/Instapaper integration** (15-20 hours)
   - API integration
   - Auto-conversion workflow

6. **Credential storage system** (20-25 hours)
   - Security implementation
   - Multi-site auth support

## 📈 **Impact vs Effort**

```
High Impact, Low Effort:    Priority 1-2 (Do First!)
High Impact, High Effort:   Priority 12 (Plan Carefully)
Low Impact, Low Effort:     Priority 7-9 (Fill Time)
Low Impact, High Effort:    Priority 13-17 (Avoid/Delay)
```

---
**Legend:**
- ★★★★★ = Critical (affects daily usage)
- ★★★★☆ = High (significant improvement)
- ★★★☆☆ = Medium (nice to have)
- ★★☆☆☆ = Low (future consideration)
- ★☆☆☆☆ = Backlog (eventually)