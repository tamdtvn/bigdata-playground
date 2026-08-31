# The structure:
    docs/
    │
    ├── roadmap.md          ← The entire route
    ├── progress.md         ← Short journal entry after each Sprint
    ├── architecture.md     ← Current Architecture
    │
    ├── adr/
    │   ├── ADR-001-repository-structure.md
    │   └── ADR-002-...
    │
    ├── sprints/
    │   ├── sprint-00.md    ← Goal, Tasks, DoD, Lessons Learned
    │   ├── sprint-01.md
    │   └── ...
    │
    └── diagrams/           ← Draw.io, Mermaid, PNG...


# General Principles:

    | File                   | Vai trò          | Tần suất            |
    | ---------------------- | ---------------- | ------------------- |
    | `roadmap.md`           | Toàn bộ lộ trình | Chỉ khi roadmap đổi |
    | `progress.md`          | Nhật ký rất ngắn | Cuối Sprint         |
    | `sprints/sprint-XX.md` | Chi tiết Sprint  | Trong Sprint        |
    | `glossary.md`          | Thuật ngữ mới    | Khi xuất hiện       |

    `architecture.md`, `ADR` và `diagrams/` chỉ cập nhật khi thực sự có thay đổi.

# Constraints
    Software Architecture
            │
            ├── Real projects
            ├── Architecture reasoning
            ├── System Design
            ├── Architectural Vocabulary
            ├── Big Data / Distributed Systems
            └── AI-assisted Engineering    

# Emergency

## 屯 — TRUÂN
    Something new is emerging, but it is not mature yet.

## THỜI
    Architecture opportunity có thể đang hình thành, chưa chắc có title rõ ràng.

## VỊ
    Bạn đã ở vị trí nhận những problem ngày càng system-level hơn.

## TRUNG
    Không đòi title ngay. Nhưng cũng không chấp nhận execution-only quá lâu.

## EVIDENCE TO WATCH
    Problem scope ↑
    Decision authority ↑
    Cross-system responsibility ↑
    Architecture artifacts ↑
    Technical influence ↑

## DECISION
    Nếu các chỉ số này tiếp tục ↑ → ở lại, tận dụng.
    Nếu chúng đứng yên hoặc ↓ trong thời gian đủ dài → cân nhắc môi trường khác.   

# MESSAGE

## Emergency + Constraints = Architecture                 