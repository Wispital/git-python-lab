CREATE TABLE IF NOT EXISTS line_counts (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    file_name text NOT NULL,
    non_empty_lines integer NOT NULL CHECK (non_empty_lines >= 0),
    created_at timestamptz NOT NULL DEFAULT now()
);
