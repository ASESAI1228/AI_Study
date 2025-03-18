-- 契約書タイプテーブル
CREATE TABLE IF NOT EXISTS contract_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

-- 取引先テーブル
CREATE TABLE IF NOT EXISTS counterparties (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    address TEXT,
    contact_person VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20)
);

-- 契約書テーブル
CREATE TABLE IF NOT EXISTS contracts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    contract_type_id INTEGER REFERENCES contract_types(id),
    counterparty_id INTEGER REFERENCES counterparties(id),
    status VARCHAR(50) DEFAULT '下書き',
    effective_date DATE,
    expiration_date DATE,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- サンプルデータ
INSERT INTO contract_types (name, description) VALUES
    ('秘密保持契約', '機密情報の取り扱いに関する契約'),
    ('業務委託契約', '業務の委託に関する契約'),
    ('ライセンス契約', '知的財産の使用許諾に関する契約'),
    ('売買契約', '物品の売買に関する契約');

INSERT INTO counterparties (name, address, contact_person, email, phone) VALUES
    ('株式会社テックイノベーション', '東京都千代田区丸の内1-1-1', '山田太郎', 'yamada@tech-innovation.co.jp', '03-1234-5678'),
    ('株式会社法務パートナーズ', '東京都港区六本木6-6-6', '鈴木一郎', 'suzuki@legal-partners.co.jp', '03-8765-4321'),
    ('グローバルコンサルティング株式会社', '大阪府大阪市北区梅田2-2-2', '佐藤花子', 'sato@global-consulting.co.jp', '06-2345-6789');

INSERT INTO contracts (title, contract_type_id, counterparty_id, status, effective_date, expiration_date, content) VALUES
    ('テックイノベーション社との秘密保持契約', 1, 1, '締結済み', '2023-01-15', '2024-01-14', '秘密保持契約書の内容がここに入ります。'),
    ('法務パートナーズ社への業務委託契約', 2, 2, 'レビュー中', '2023-02-20', '2023-08-19', '業務委託契約書の内容がここに入ります。'),
    ('グローバルコンサルティング社とのライセンス契約', 3, 3, '下書き', '2023-03-10', '2025-03-09', 'ライセンス契約書の内容がここに入ります。'); 