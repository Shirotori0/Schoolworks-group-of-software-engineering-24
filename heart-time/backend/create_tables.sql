-- 设置客户端字符集
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;
SET CHARACTER_SET_CLIENT = utf8mb4;
SET CHARACTER_SET_RESULTS = utf8mb4;

-- 创建数据库
CREATE DATABASE IF NOT EXISTS emotion_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE emotion_system;

-- 用户表
CREATE TABLE IF NOT EXISTS user_info (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    user_openid VARCHAR(64) NOT NULL COMMENT '微信OpenID',
    nickname VARCHAR(32) NULL COMMENT '用户昵称',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE KEY uk_user_openid (user_openid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户信息表';

-- AI角色表
CREATE TABLE IF NOT EXISTS ai_role (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '角色ID',
    role_name VARCHAR(32) NOT NULL COMMENT '角色名称',
    gentleness DECIMAL(3,2) NOT NULL DEFAULT 0.80 COMMENT '温柔度(0-1)',
    rationality DECIMAL(3,2) NOT NULL DEFAULT 0.50 COMMENT '理性值(0-1)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI角色表';

-- 情绪日记表
CREATE TABLE IF NOT EXISTS emotion_diary (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '日记ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    diary_content TEXT NOT NULL COMMENT '日记内容',
    voice_oss_path VARCHAR(128) NULL COMMENT '语音OSS路径',
    emotion_tags VARCHAR(255) NULL COMMENT '情绪标签',
    ai_summary TEXT NULL COMMENT 'AI内容总结',
    ai_reply TEXT NULL COMMENT 'AI共情回复',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_user_id_create_time (user_id, create_time),
    FOREIGN KEY (user_id) REFERENCES user_info(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='情绪日记表';

-- 角色对话表
CREATE TABLE IF NOT EXISTS role_chat (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '对话ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    role_id BIGINT NOT NULL COMMENT '角色ID',
    user_input TEXT NOT NULL COMMENT '用户输入',
    ai_reply TEXT NOT NULL COMMENT 'AI回复',
    chat_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '对话时间',
    INDEX idx_user_id_chat_time (user_id, chat_time),
    FOREIGN KEY (user_id) REFERENCES user_info(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES ai_role(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色对话表';

-- 情绪轨迹表
CREATE TABLE IF NOT EXISTS emotion_track (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '轨迹ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    track_date DATE NOT NULL COMMENT '日期',
    anxiety_value INT NOT NULL DEFAULT 0 COMMENT '焦虑值',
    joy_value INT NOT NULL DEFAULT 0 COMMENT '愉悦值',
    key_event VARCHAR(255) NULL COMMENT '关键事件',
    UNIQUE KEY uk_user_id_track_date (user_id, track_date),
    INDEX idx_user_id_track_date (user_id, track_date),
    FOREIGN KEY (user_id) REFERENCES user_info(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='情绪轨迹表';

-- 插入示例AI角色数据
INSERT INTO ai_role (role_name, gentleness, rationality) VALUES
('暖心朋友', 0.90, 0.40),
('理性顾问', 0.50, 0.90),
('温柔导师', 0.85, 0.60);
