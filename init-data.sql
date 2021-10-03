CREATE TABLE tb_trx_src
(
    id SERIAL NOT NULL,
    creation_date date,
    sale_value bigint NOT NULL
);
    
INSERT INTO tb_trx_src(creation_date, sale_value) VALUES
 (current_date, random() * 100),
 (current_date, random() * 100),
 (current_date, random() * 100),
 (current_date, random() * 100),
 (current_date, random() * 100),
 (current_date, random() * 100),
 (current_date, random() * 100),
 (current_date, random() * 100),
 (current_date, random() * 100),
 (current_date, random() * 100)