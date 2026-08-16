The structure:

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


Quy tắc chung:

| File                   | Vai trò          | Tần suất            |
| ---------------------- | ---------------- | ------------------- |
| `roadmap.md`           | Toàn bộ lộ trình | Chỉ khi roadmap đổi |
| `progress.md`          | Nhật ký rất ngắn | Cuối Sprint         |
| `sprints/sprint-01.md` | Chi tiết Sprint  | Trong Sprint        |
| `glossary.md`          | Thuật ngữ mới    | Khi xuất hiện       |

`architecture.md`, `ADR` và `diagrams/` chỉ cập nhật khi thực sự có thay đổi.