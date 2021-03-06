
CREATE PROCEDURE [dbo].Restart_Summary
	@dbname NVARCHAR(100),
	@appendage NVARCHAR(255)
AS

declare @sql nvarchar(3000);
set @sql = 
N'USE '+QUOTENAME(@dbname)+ N';
IF OBJECT_ID(''dbo.SummaryRDF_'+@appendage+N''', ''U'') IS NOT NULL
	DROP TABLE [dbo].[SummaryRDF_'+@appendage+N'];
CREATE TABLE [dbo].[SummaryRDF_'+@appendage+N']
( [Subject] varchar(255) NOT NULL,
	[Object] varchar(255) NOT NULL,
	CONSTRAINT pk_summary'+@appendage+N' PRIMARY KEY ([Subject],[Object]) );

CREATE INDEX s_index
ON [dbo].[SummaryRDF_'+@appendage+N'] ([Subject]);
CREATE INDEX o_index
ON [dbo].[SummaryRDF_'+@appendage+N'] ([Object]);

IF OBJECT_ID(''dbo.SummaryONAME2SNODE_'+@appendage+N''', ''U'') IS NOT NULL
	DROP TABLE [dbo].[SummaryONAME2SNODE_'+@appendage+N'];
CREATE TABLE [dbo].[SummaryONAME2SNODE_'+@appendage+N']
(
	[Original_name] varchar(255) NOT NULL,
	[Snode] varchar(255) NOT NULL,
	Primary Key(Original_name) );

IF OBJECT_ID(''dbo.SummaryCorrections_'+@appendage+N''', ''U'') IS NOT NULL
	DROP TABLE [dbo].[SummaryCorrections_'+@appendage+N'];
CREATE TABLE [dbo].[SummaryCorrections_'+@appendage+N']
(
	[PosOrNeg] varchar(2) NOT NULL,
	[Subject] varchar(255) NOT NULL,
	[Object] varchar(255) NOT NULL,
	CONSTRAINT pk_corrections'+@appendage+N' PRIMARY KEY ([Subject],[Object]) );

CREATE INDEX s_index
ON [dbo].[SummaryCorrections_'+@appendage+N'] ([Subject]);
CREATE INDEX o_index
ON [dbo].[SummaryCorrections_'+@appendage+N'] ([Object]);';

EXEC (@sql);


GO
