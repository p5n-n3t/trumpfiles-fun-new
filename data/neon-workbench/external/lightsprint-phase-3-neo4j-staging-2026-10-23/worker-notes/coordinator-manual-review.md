# Coordinator manual relationship inspection

The coordinator read these 20 output relationships and compared the indicated values with the original SQLite rows using read-only immutable connections. These checks establish faithful projection, not claim truth or source availability. Four evenly spaced stable-ID samples per supported type cover different entries and preserve the direction and origin.

| Relationship ID | Type | Entry | Target | Checked basis |
| --- | --- | ---: | --- | --- |
| rel:0055102262c5d23013ac3e8d | MENTIONS | 6302 | Sergei Lavrov | entity_entry_links role=mentioned and explicit entity ID |
| rel:5527830369114c5799f0f1f0 | MENTIONS | 6806 | Donald Trump | entity_entry_links role=mentioned and explicit entity ID |
| rel:aa6f4cd74a0c6300014d0308 | MENTIONS | 6664 | Xi Jinping | entity_entry_links role=mentioned and explicit entity ID |
| rel:fff5a8769eef14f70c063def | MENTIONS | 6414 | Donald Trump | entity_entry_links role=mentioned and explicit entity ID |
| rel:00004217c3cfb5a70883d0a0 | SOURCED_FROM | 386 | Donald Trump falsely says 'Biden FBI' placed agents in Jan. 6 crowds | explicit HTTPS URL in trump_sources or entry.sources; entry 2264 has sources[0].url=https://www.bbc.com/news/articles/ce84z6y3ke4o |
| rel:5602d8548b799c14c057861e | SOURCED_FROM | 2264 | What we know about the US and Iran ceasefire deal | explicit HTTPS URL in trump_sources or entry.sources; entry 2264 has sources[0].url=https://www.bbc.com/news/articles/ce84z6y3ke4o |
| rel:aa014823e51cac7692f03297 | SOURCED_FROM | 2163 | Poll: Most say Iran war not going well, but don't want regime left in power | explicit HTTPS URL in trump_sources or entry.sources; entry 2264 has sources[0].url=https://www.bbc.com/news/articles/ce84z6y3ke4o |
| rel:fff8f6e64b945864e20dc887 | SOURCED_FROM | 2273 | Donald Trump says ‘a whole civilisation will die’ if Iran ignores demands | explicit HTTPS URL in trump_sources or entry.sources; entry 2264 has sources[0].url=https://www.bbc.com/news/articles/ce84z6y3ke4o |
| rel:0005a6d2763573f978519e00 | HAS_THEME | 3321 | election pressure | exact trump_keywords.keyword and/or entry.keywords value |
| rel:56a16ce63a7746809a8ce1e8 | HAS_THEME | 2391 | authoritarianism | exact trump_keywords.keyword and/or entry.keywords value |
| rel:ac2dbdd8b81e796539dd7dd8 | HAS_THEME | 1492 | durable challenge | exact trump_keywords.keyword and/or entry.keywords value |
| rel:ffff55f04068dd81fa0535ef | HAS_THEME | 3584 | iran conflict | exact trump_keywords.keyword and/or entry.keywords value |
| rel:0003bf269b056e18b667b855 | IN_CATEGORY | 3895 | Human Rights Violations | exact frozen trump_entries.category |
| rel:5539065ef37659da3da47cb3 | IN_CATEGORY | 5220 | Grift / Financial Exploitation | exact frozen trump_entries.category |
| rel:acc455e1fed05f27b100ed26 | IN_CATEGORY | 755 | Foreign Policy | exact frozen trump_entries.category |
| rel:fff4492e09637bad29b5fd95 | IN_CATEGORY | 1740 | Government Corruption | exact frozen trump_entries.category |
| rel:00042071a8b627d5f90fc136 | IN_PHASE | 2398 | Post-Presidency | exact frozen trump_entries.phase |
| rel:5575ae7ad59f6a9f390b484e | IN_PHASE | 3650 | White House 2 | exact frozen trump_entries.phase |
| rel:abd7ef91f449db24f4dd0f51 | IN_PHASE | 4637 | White House 2:2 | exact frozen trump_entries.phase |
| rel:fffe9b2f68ce26984f4c8f2d | IN_PHASE | 4788 | White House 2:2 | exact frozen trump_entries.phase |

No ACTOR_IN, TARGET_OF, SAME_AS, PRECEDES or RELATES_TO edge was invented to create examples. The inputs do not provide sufficiently reviewed evidence for those types. The independent QA and relationship workers record additional samples in their own notes.
