/****** Script for SelectTopNRows command from SSMS  ******/
USE DBLP4;
WITH org_nodes(name) AS
( SELECT [Original_name] FROM [dbo].[SummaryONAME2SNODE_NonUniformDBLP4] )

SELECT s.name, SUM(s.cnt)
FROM
(
(SELECT n.[name] as name, 0 as cnt FROM org_nodes n)
UNION
(
SELECT n.[name] as name ,COUNT(*) as cnt
FROM org_nodes n, [dbo].[SummaryCorrections_NonUniformDBLP4] c
WHERE n.name = c.[Subject] OR n.name = c.[Object]
GROUP BY n.name)
)
s
GROUP BY s.name