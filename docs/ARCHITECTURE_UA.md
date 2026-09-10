# Архітектура застосунку «Менеджер витрат»

## 1. Загальний опис

«Менеджер витрат» — це навчальний настільний застосунок для обліку особистих
фінансів. Користувач може задати початковий баланс, додавати доходи та витрати,
фільтрувати витрати за датою, переглядати графіки, прогноз балансу й автоматично
сформовані повідомлення.

Проєкт має **шарову архітектуру**. Код поділено на кілька частин із різною
відповідальністю:

- **UI-шар** створює вікна та віджети за допомогою `ttkbootstrap` і відображає
  графіки `matplotlib`.
- **Доменний шар** містить основні сутності предметної області: баланс, дохід,
  витрату, категорію та знімок балансу. Сутності самі перевіряють свої інваріанти.
- **Сервісний шар** координує зміни доменної моделі та їх збереження.
- **Шар обчислень** готує дані для графіків, прогнозу й інформаційних повідомлень.
- **Шар збереження** записує дані в SQLite і відновлює їх під час наступного запуску.
- **Конфігурація** вибирає `dev` або `test` режим і містить централізовані константи.

Це не сувора реалізація MVC. Найточніше проєкт можна описати як невеликий
шаровий застосунок із доменною моделлю та патерном **Repository**.

## 2. Архітектурна діаграма

```mermaid
flowchart TB
    User[Користувач]

    subgraph Presentation[UI-шар — ttkbootstrap та matplotlib]
        MainWindow[MainWindow]
        InitialDialog[InitialBalanceWindow]
        Sidebar[Sidebar]
        Charts[GraphChart і PieChart]
        ExpenseTable[ExpenseTable]
        Alerts[DashboardAlerts і Alert]
        DateSelector[DateRangeSelector]
    end

    subgraph ApplicationLogic[Координація застосунку]
        FinanceService[FinanceService]
    end

    subgraph Domain[Доменний шар]
        Balance[Balance]
        Expense[Expense]
        Income[Income]
        Snapshot[BalanceSnapshot]
        Category[Category]
    end

    subgraph Calculations[Шар обчислень]
        ExpenseUtils[expense_utils]
        DashboardUtils[dashboard_utils]
    end

    subgraph Persistence[Шар збереження]
        RepositoryContract[BalanceRepository Protocol]
        Repository[SQLiteBalanceRepository]
        MockData[mock_data]
        Database[(SQLite)]
    end

    subgraph Configuration[Конфігурація]
        Env[.env + профілі]
        Config[config.py]
        Constants[constants.py]
    end

    User --> MainWindow
    MainWindow --> InitialDialog
    MainWindow --> Sidebar
    MainWindow --> Charts
    MainWindow --> ExpenseTable
    MainWindow --> Alerts
    MainWindow --> DateSelector
    MainWindow --> FinanceService
    Sidebar --> FinanceService
    MainWindow --> ExpenseUtils
    MainWindow --> DashboardUtils
    Balance --> Expense
    Balance --> Income
    Balance --> Snapshot
    FinanceService --> Balance
    FinanceService --> RepositoryContract
    Repository -.->|реалізує| RepositoryContract
    Repository --> Balance
    Repository --> Category
    Repository <--> Database
    MockData --> Repository
    Env --> Config
    Config --> MainWindow
    FinanceService --> MockData
    Constants --> Presentation
    Constants --> Calculations
```

### Як читати цю діаграму

`MainWindow` координує лише компоненти інтерфейсу. Операції користувача передаються
до `FinanceService`, який працює з `Balance` через абстракцію `BalanceRepository`.
Інтерфейс і доменна модель не виконують SQL-запити напряму.

## 3. Діаграма класів

```mermaid
classDiagram
    class MainWindow {
        -window
        -balance: Balance
        -finance_service: FinanceService
        -sidebar: Sidebar
        -top_chart: GraphChart
        -pie_chart: PieChart
        -future_chart: GraphChart
        -expense_table: ExpenseTable
        -dashboard_alerts: DashboardAlerts
        +setup()
        +update_charts()
        +start()
    }

    class Balance {
        -value: Decimal
        -expenses: list
        -incomes: list
        -value_snapshots: list
        +get_value()
        +get_expenses()
        +get_incomes()
        +get_value_snapshots()
        +add_expense(expense)
        +add_income(income)
    }

    class Expense {
        +date: date
        +category: str
        +amount: Decimal
    }

    class Income {
        +date: date
        +amount: Decimal
    }

    class BalanceSnapshot {
        +date: date
        +value: Decimal
    }

    class Category {
        +name: str
        +description: str
    }

    class SQLiteBalanceRepository {
        +database_path: Path
        +create_balance(value, created_at) Balance
        +load_balance() Balance
        +save_expense(expense, new_balance, snapshot)
        +save_income(income, new_balance, snapshot)
        +load_categories() list
        +clear_financial_data()
    }

    class BalanceRepository {
        <<Protocol>>
        +create_balance(value) Balance
        +load_balance() Balance
        +save_expense(...)
        +save_income(...)
    }

    class FinanceService {
        -repository: BalanceRepository
        -balance: Balance
        +initialize(mode, reset, initial_balance) Balance
        +add_expense(amount, category, date)
        +add_income(amount, date)
        +get_categories() list
    }

    class Sidebar {
        -finance_service: FinanceService
        -expense_categories: list
        -on_balance_changed: Callable
        +draw()
    }

    class InitialBalanceWindow {
        -result: Decimal|None
        +draw()
        +submit()
        +get_result() Decimal|None
    }

    class GraphChart {
        -figure
        -axis
        -tk_canvas
        +draw()
        +update(x_data, y_data)
    }

    class PieChart {
        -sizes: list
        -categories: list
        -colors: list
        +draw()
        +update(sizes, categories, colors)
    }

    class ExpenseTable {
        -balance: Balance
        -expense_view
        +draw()
        +update(expenses, start_date, end_date)
    }

    class DateRangeSelector {
        -from_date_entry
        -to_date_entry
        -on_change: Callable
        +draw()
        +get_date_range()
    }

    class DashboardAlerts {
        -balance: Balance
        -alerts: list
        +draw()
        +update()
    }

    class Alert {
        -text: str
        -style: str
        +draw()
        +update(text, style)
    }

    MainWindow *-- Sidebar
    MainWindow *-- GraphChart
    MainWindow *-- PieChart
    MainWindow *-- ExpenseTable
    MainWindow *-- DateRangeSelector
    MainWindow *-- DashboardAlerts
    MainWindow ..> InitialBalanceWindow
    MainWindow --> FinanceService
    MainWindow --> Balance
    Sidebar --> FinanceService
    DashboardAlerts --> Balance
    DashboardAlerts *-- Alert
    ExpenseTable --> Balance
    Balance "1" o-- "0..*" Expense
    Balance "1" o-- "0..*" Income
    Balance "1" o-- "1..*" BalanceSnapshot
    FinanceService --> Balance
    FinanceService --> BalanceRepository
    SQLiteBalanceRepository ..|> BalanceRepository
    SQLiteBalanceRepository ..> Category : завантажує
```

### Головні відповідальності класів

- `MainWindow` створює UI-компоненти та координує їх оновлення.
- `FinanceService` виконує сценарії запуску, додавання доходу чи витрати та
  координує доменну модель зі сховищем.
- `Balance` містить поточний фінансовий стан і змінює його після доходів або витрат.
- `SQLiteBalanceRepository` приховує всі деталі роботи з SQLite.
- `Sidebar` приймає дані користувача й передає команду до `FinanceService`.
- `GraphChart`, `PieChart` та `ExpenseTable` лише відображають підготовлені дані.
- `dashboard_utils` і `expense_utils` не створюють інтерфейс, а виконують
  обчислення.

## 4. Діаграми послідовності

### 4.1. Запуск застосунку

```mermaid
sequenceDiagram
    actor User as Користувач
    participant Entry as main.py
    participant Config as config.py
    participant Window as MainWindow
    participant Service as FinanceService
    participant Repo as SQLiteBalanceRepository
    participant DB as SQLite
    participant Mock as mock_data
    participant Dialog as InitialBalanceWindow
    participant UI as UI-компоненти

    User->>Entry: Запускає застосунок
    Entry->>Config: Читає APP_MODE та профіль .env
    Entry->>Repo: Створює репозиторій
    Repo->>DB: Створює таблиці, якщо їх немає
    Entry->>Service: Створює FinanceService(repository)
    Entry->>Window: Створює MainWindow(service)
    Window->>Service: initialize(mode, reset)
    Service->>Repo: load_balance()
    Repo->>DB: Читає стан і транзакції

    alt APP_MODE = test
        Service->>Mock: load_mock_data(repository)
        Mock->>Repo: Очищає лише тестові фінансові дані
        Mock->>Repo: Записує баланс, доходи та витрати
        Repo->>DB: Зберігає тестові сутності
    else APP_MODE = dev і баланс існує
        Repo-->>Service: Повертає відновлений Balance
    else APP_MODE = dev і це перший запуск
        Window->>Dialog: Показує запит початкового балансу
        Dialog-->>User: Поле введення
        User->>Dialog: Вводить баланс
        Dialog-->>Window: Повертає значення
        Window->>Service: initialize(..., value)
        Service->>Repo: create_balance(value)
        Repo->>DB: Зберігає стан і перший знімок
    end

    Window->>UI: Створює сайдбар, графіки, таблицю та повідомлення
    UI-->>User: Показує готове головне вікно
```

### 4.2. Додавання витрати

```mermaid
sequenceDiagram
    actor User as Користувач
    participant Sidebar
    participant Service as FinanceService
    participant Balance
    participant Repo as SQLiteBalanceRepository
    participant DB as SQLite
    participant Window as MainWindow
    participant Calc as Обчислення
    participant Views as Графіки, таблиця та сповіщення

    User->>Sidebar: Натискає «Витрата»
    Sidebar-->>User: Показує форму
    User->>Sidebar: Обирає категорію та вводить суму
    Sidebar->>Service: add_expense(amount, category)
    Service->>Service: Створює Expense і майбутній snapshot
    Service->>Repo: save_expense(expense, balance, snapshot)
    Repo->>DB: BEGIN + INSERT expense
    Repo->>DB: UPDATE current_balance
    Repo->>DB: INSERT balance_snapshot + COMMIT
    Repo-->>Service: Збереження успішне
    Service->>Balance: add_expense(expense)
    Sidebar->>Window: on_balance_changed()
    Window->>Calc: Готує статистику й прогноз
    Calc-->>Window: Дані для відображення
    Window->>Views: update(...)
    Views-->>User: Показує новий баланс і аналітику
```

Для доходу послідовність така сама, але створюється `Income`, а сума додається до
балансу через `add_income()` і `save_income()`.

## 5. Діаграма бази даних

```mermaid
erDiagram
    APP_STATE {
        INTEGER id PK "завжди 1"
        INTEGER initial_balance "копійки"
        INTEGER current_balance "копійки"
        TEXT created_at
    }

    CATEGORIES {
        TEXT name PK
        TEXT description
    }

    EXPENSES {
        INTEGER id PK
        TEXT occurred_on
        TEXT category FK
        INTEGER amount "копійки"
    }

    INCOMES {
        INTEGER id PK
        TEXT occurred_on
        INTEGER amount "копійки"
    }

    BALANCE_SNAPSHOTS {
        INTEGER id PK
        TEXT occurred_at
        INTEGER value "копійки"
    }

    SCHEMA_METADATA {
        TEXT key PK
        TEXT value
    }

    CATEGORIES ||--o{ EXPENSES : "має"
    APP_STATE ||--o{ EXPENSES : "логічно включає"
    APP_STATE ||--o{ INCOMES : "логічно включає"
    APP_STATE ||--o{ BALANCE_SNAPSHOTS : "логічно включає"
```

`APP_STATE` — singleton-таблиця: застосунок зберігає один активний баланс у рядку
з `id = 1`. Фізичний зовнішній ключ зараз є лише між `EXPENSES.category` і
`CATEGORIES.name`. Зв'язки інших фінансових таблиць з `APP_STATE` є логічними,
оскільки застосунок поки підтримує лише одного користувача й один баланс.
Грошові значення зберігаються як цілі копійки, а `SCHEMA_METADATA` позначає версію
формату та дозволяє один раз перетворити старі значення типу `REAL`.

## 6. Потік даних

1. Користувач вводить дані у вікні `Sidebar`.
2. `Sidebar` передає суму й категорію до `FinanceService`.
3. Сервіс створює валідований `Expense` або `Income` і розраховує новий стан.
4. `SQLiteBalanceRepository` атомарно записує транзакцію, новий баланс і snapshot.
5. Після успішного запису сервіс оновлює `Balance` у пам'яті.
6. `MainWindow.update_charts()` повторно готує дані.
7. Графіки, таблиця та повідомлення перемальовуються.

Такий порядок важливий: якщо SQLite не зможе зберегти операцію, інтерфейс не
показуватиме незбережений баланс.

## 7. Режими dev і test

```mermaid
flowchart LR
    Env[APP_MODE у .env] --> Choice{Який режим?}
    Choice -->|dev| DevDB[(expense_manager.db)]
    Choice -->|test| Reset[Скидання тестових даних]
    Reset --> Seed[Генерація даних за 6 місяців]
    Seed --> TestDB[(test_expense_manager.db)]
    DevDB --> Dashboard[Головне вікно]
    TestDB --> Dashboard
```

- `dev` — реальний сценарій використання. Дані не скидаються між запусками.
- `test` — демонстраційний сценарій. Окрема база щоразу наповнюється передбачуваними
  тестовими даними, тому графіки та повідомлення можна перевірити одразу.

## 8. Сильні сторони архітектури

- Код поділено за відповідальністю, тому його простіше читати початківцю.
- UI не містить SQL-запитів.
- Дані зберігаються атомарно й відновлюються після перезапуску.
- Гроші обчислюються через `Decimal`, а в SQLite зберігаються як цілі копійки.
- Доменні колекції захищені від зміни ззовні, а сутності є незмінними.
- Залежність від сховища описана через `BalanceRepository Protocol`.
- Автоматичні тести перевіряють домен, обчислення, SQLite та міграцію даних.
- Обчислення прогнозу та статистики відокремлені від віджетів.
- `test` режим дозволяє швидко продемонструвати всі частини інтерфейсу.
- Текст, стилі та розміри зібрані у `constants.py`.

## 9. Обмеження та можливі покращення

Для навчального pet project поточна архітектура є достатньою, але її можна
розвивати далі:

1. Додати ідентифікатор балансу до фінансових таблиць для підтримки кількох
   користувачів або рахунків.
2. Додати редагування й видалення доходів та витрат.
3. Розширити механізм міграцій для наступних версій схеми.
4. Реалізувати експорт CSV, кнопка якого вже присутня в інтерфейсі.

## 10. Коротке пояснення для захисту проєкту

> Застосунок побудовано за шаровим принципом. Інтерфейс на ttkbootstrap приймає
> дії користувача, FinanceService координує сценарії, а доменний клас Balance
> керує фінансовим станом. Окремі функції виконують аналітичні обчислення, а
> SQLiteBalanceRepository реалізує контракт BalanceRepository та зберігає сутності
> в SQLite. MainWindow оновлює графіки, таблицю й
> повідомлення після кожної операції. Dev-режим працює з реальними даними, а
> test-режим автоматично завантажує демонстраційний набір за шість місяців.
