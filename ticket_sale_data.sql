-- ticket_sales_query.sql

-- This query retrieves the total number of tickets sold for all events
-- along with event details such as event ID, name, date, and total tickets available.
-- The results are grouped by event ID and sorted by the total tickets sold in descending order.
-- Only the top 3 events by tickets sold are returned.

SELECT 
    e.id AS event_id,                -- Event ID
    e.name AS event_name,            -- Name of the event
    e.date AS event_date,            -- Date of the event
    e.total_tickets AS total_tickets, -- Total tickets available for the event
    COALESCE(SUM(t.quantity), 0) AS tickets_sold -- Total tickets sold, defaults to 0 if none sold
FROM 
    Event e
LEFT JOIN 
    Ticket t ON e.id = t.event_id    -- Join Ticket table on event ID
GROUP BY 
    e.id                              -- Group results by event ID
ORDER BY 
    tickets_sold DESC                 -- Order by total tickets sold in descending order
LIMIT 3;                             -- Limit results to the top 3 events
