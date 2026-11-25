SELECT id, file_name, non_empty_lines FROM line_counts ORDER BY id;
SELECT file_name, non_empty_lines FROM line_counts
WHERE non_empty_lines >= 3 ORDER BY non_empty_lines DESC;
SELECT file_name, COUNT(*) AS runs, AVG(non_empty_lines) AS avg_lines
FROM line_counts GROUP BY file_name ORDER BY runs DESC, file_name;
