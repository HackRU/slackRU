CREATE TABLE IF NOT EXISTS projects(
    id CHAR(5),
    project_name VARCHAR(500),
    project_desc VARCHAR(3000),
    author VARCHAR(300),
    skills_have VARCHAR(1000),
    skills_wanted VARCHAR(1000),
    team_size INTEGER,
    timestamp FLOAT,
    status INTEGER
);
