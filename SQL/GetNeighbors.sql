-- ================================================
-- Template generated from Template Explorer using:
-- Create Procedure (New Menu).SQL
--
-- Use the Specify Values for Template Parameters 
-- command (Ctrl-Shift-M) to fill in the parameter 
-- values below.
--
-- This block of comments will not be included in
-- the definition of the procedure.
-- ================================================
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:		<Author,,Name>
-- Create date: <Create Date,,>
-- Description:	<Description,,>
-- =============================================
USE [wordnet]
GO
CREATE PROCEDURE [dbo].[GetNeighbors] 
	@uri nvarchar(250),
	@table nvarchar(250)
AS
BEGIN

declare @snode nvarchar(250);
WITH mapping(o_name,snode) AS
(
	(SELECT * FROM [dbo].[SummaryONAME2SNODE_Alteredwordnet_50_100_1] WHERE @table = 'Altered')
	UNION
	(SELECT * FROM [dbo].[SummaryONAME2SNODE_NonUniformwordnetSecondHeuristic] WHERE @table = 'NonUniformSecondHeuristic')
	UNION
	(SELECT * FROM [dbo].[SummaryONAME2SNODE_Purewordnet] WHERE @table = 'Pure')
)

SELECT @snode = [snode] FROM mapping WHERE o_name = @uri;

WITH corrections(posOrNeg,[Subject],[Object]) AS
(
	(SELECT * FROM [dbo].[SummaryCorrections_Alteredwordnet_50_100_1] WHERE @table = 'Altered'
		AND ([Subject] = @uri OR [Object] = @uri))
	UNION
	(SELECT * FROM [dbo].[SummaryCorrections_NonUniformwordnetSecondHeuristic] WHERE @table = 'NonUniformSecondHeuristic'
		AND ([Subject] = @uri OR [Object] = @uri))
	UNION
	(SELECT * FROM [dbo].[SummaryCorrections_Purewordnet] WHERE @table = 'Pure'
		AND ([Subject] = @uri OR [Object] = @uri))
),
mapping(o_name,snode) AS
(
	(SELECT * FROM [dbo].[SummaryONAME2SNODE_Alteredwordnet_50_100_1] WHERE @table = 'Altered')
	UNION
	(SELECT * FROM [dbo].[SummaryONAME2SNODE_NonUniformwordnetSecondHeuristic] WHERE @table = 'NonUniformSecondHeuristic')
	UNION
	(SELECT * FROM [dbo].[SummaryONAME2SNODE_Purewordnet] WHERE @table = 'Pure')
),
summary([Subject],[Object]) AS
(
	(SELECT * FROM [dbo].[SummaryRDF_Alteredwordnet_50_100_1] WHERE @table = 'Altered')
	UNION
	(SELECT * FROM [dbo].[SummaryRDF_NonUniformwordnetSecondHeuristic] WHERE @table = 'NonUniformSecondHeuristic')
	UNION
	(SELECT * FROM [dbo].[SummaryRDF_Purewordnet] WHERE @table = 'Pure')
)


(SELECT c.[Subject]
FROM corrections c
WHERE c.posOrNeg = '+'
AND c.[Object] = @uri)
UNION
(SELECT c.[Object]
FROM corrections c
WHERE c.posOrNeg = '+'
AND c.[Subject] = @uri)
UNION
( ((SELECT m.o_name
	FROM summary s, mapping m
	WHERE s.[Subject] = @snode
		AND s.[Object] = m.snode)
	UNION
	(
		SELECT m.o_name
		FROM summary s, mapping m
		WHERE s.[Object] = @snode
			AND s.[Subject] = m.snode
	))
	EXCEPT
	(
		(SELECT c.[Subject]
		FROM corrections c
		WHERE c.posOrNeg = '-'
		AND c.[Object] = @uri)
		UNION
		(SELECT c.[Object]
		FROM corrections c
		WHERE c.posOrNeg = '-'
		AND c.[Subject] = @uri)
	)
)
;

END