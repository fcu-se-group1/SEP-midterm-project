-- 1. 使用者資料表 (User)
CREATE TABLE User (
    user_id INT PRIMARY KEY,
    role VARCHAR(20) NOT NULL,     -- 使用者身分（學生、教師、行政人員）
    class VARCHAR(50)              -- 班級名稱（僅學生適用）
);

-- 2. 課程資料表 (Course)
CREATE TABLE Course (
    course_code INT PRIMARY KEY,                 -- 課程編號
    course_name VARCHAR(100) NOT NULL,           -- 課程名稱
    credits INT NOT NULL,                        -- 學分數
    max_students INT NOT NULL,                   -- 最大修課人數
    instructor_name VARCHAR(50),                 -- 教師姓名
    location VARCHAR(50),                        -- 上課地點
    is_mandatory BOOLEAN NOT NULL                -- 必修或選修（布林值）
);

-- 3. 課程時間資料表 (Course_Schedule)
-- 使用組合鍵（course_code, weekday, time_slot）表示每一門課的上課時間（星期與節次）
CREATE TABLE Course_Schedule (
    course_code INT,                             -- 課程編號
    weekday VARCHAR(10) NOT NULL,                -- 上課星期（如 "星期一"）
    time_slot VARCHAR(20) NOT NULL,              -- 節次（如 "1-2節"）
    PRIMARY KEY (course_code, weekday, time_slot),
    FOREIGN KEY (course_code) REFERENCES Course(course_code)
);

-- 4. 課程班級限制資料表 (Course_Class_Restriction)
-- 使用組合鍵（course_code, class_name）表示多個班級可以修讀該課
CREATE TABLE Course_Class_Restriction (
    course_code INT,                             -- 課程編號
    class_name VARCHAR(50),                      -- 允許的班級名稱
    PRIMARY KEY (course_code, class_name),
    FOREIGN KEY (course_code) REFERENCES Course(course_code),
    FOREIGN KEY (class_name) REFERENCES Class(class_name)
);

-- 5. 開課班級資料表 (Course_Class_Offering)
-- 使用組合鍵（course_code, class_name）表示課程的實際開課班級
CREATE TABLE Course_Class_Offering (
    course_code INT,                             -- 課程編號
    class_name VARCHAR(50),                      -- 開課班級
    PRIMARY KEY (course_code, class_name),
    FOREIGN KEY (course_code) REFERENCES Course(course_code),
    FOREIGN KEY (class_name) REFERENCES Class(class_name)
);

-- 6. 班級資料表 (Class)
CREATE TABLE Class (
    class_name VARCHAR(50) PRIMARY KEY           -- 班級名稱
);

-- 7. 地點資料表 (Location)
CREATE TABLE Location (
    location_name VARCHAR(50) PRIMARY KEY,       -- 地點名稱
    capacity INT NOT NULL                        -- 最大人數
);

-- 8. 選課資料表 (Enrollment)
-- 使用組合鍵（course_code, user_id）表示學生選課情況
CREATE TABLE Enrollment (
    course_code INT,                             -- 課程編號
    user_id INT,                                 -- 學生ID
    status VARCHAR(20) NOT NULL,                 -- 狀態（已選、待選）
    PRIMARY KEY (course_code, user_id),
    FOREIGN KEY (course_code) REFERENCES Course(course_code),
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);

-- 9. 加退選時間資料表 (EnrollmentPeriod)
CREATE TABLE EnrollmentPeriod (
    period_type VARCHAR(20) PRIMARY KEY,         -- 類別（加選、退選）
    start_time DATETIME NOT NULL,                -- 開始時間
    end_time DATETIME NOT NULL                   -- 結束時間
);
