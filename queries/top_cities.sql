-- Total amount and average completion_rate by city
SELECT
  city,
  COUNT(*)                      AS orders_count,
  SUM(amount)                   AS total_amount,
  ROUND(AVG(completion_rate),3) AS avg_completion_rate
FROM orders
GROUP BY city
ORDER BY total_amount DESC;
