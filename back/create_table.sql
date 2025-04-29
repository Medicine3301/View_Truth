CREATE TABLE content_analysis (
    -- 主鍵和基本信息
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    link VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    publish_date VARCHAR(50),
    location VARCHAR(255),
    event_type VARCHAR(50),
    
    -- 評分相關
    credibility_score DECIMAL(5,2),
    credibility_level VARCHAR(50),
    factual_score DECIMAL(5,2),
    critical_score DECIMAL(5,2),
    balanced_score DECIMAL(5,2),
    source_score DECIMAL(5,2),
    
    -- JSON 格式儲存的分析結果
    factual_analysis JSON,
    critical_analysis JSON,
    balanced_analysis JSON,
    source_analysis JSON,
    verification_guide JSON,
    
    -- 時間戳記錄
    analysis_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- 索引
    INDEX idx_credibility_score (credibility_score),
    INDEX idx_event_type (event_type),
    INDEX idx_analysis_timestamp (analysis_timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
