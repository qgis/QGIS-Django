<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="plugins">

<html>
<head>
<title>Qgis Plugins - Official 1.0 Repository</title>
<!--link href="xsl.css" rel="stylesheet" type="text/css" /-->

<style>
body  {
   font-family:Verdana, Arial, Helvetica, sans-serif;
width: 45em;
 }

div.plugin {
 background-color:#C3FbFF;
 border:1px solid #8FDF8F;
 clear:both;
 display:block;
 padding:0 0 0.5em;
 margin:1em;
}

div.head {
  background-color:#79B3Ec;
  border-bottom-width:0;
  color:#0;
  display:block;
  font-size:100%;
  font-weight:bold;
  margin:0;
  padding:0.3em 1em;
}
div.menu{
	display:block;
	text-align: left;
	font-size:100%;
	}
div.description{
  display: block;
  float:none;
  margin:0;
  text-align: left;
  padding:0.2em 0.5em 0.4em;
  color: black;
  font-size:85%;
  font-weight:normal;
 }

div.download, div.author{
  font-size: 80%;
  padding: 0em 0em 0em 1em;
 }

td.menu_panel {
 	width: 180px;
	font-size: 80%;
	}
</style>

</head>
<body>
<h2>QGIS 1.x Official Python Plugins</h2>
<p>
View <a href="/repo/contributed">user-contributed</a> plugins.
</p>
<table>
<tr>

<td valign="top" class="menu_panel">
Download:
<xsl:for-each select="/plugins/pyqgis_plugin">
<div class="menu">
<xsl:element name="a">
 <xsl:attribute name="href">
  <xsl:value-of select="download_url" />
 </xsl:attribute>
 <xsl:value-of select="@name" />
</xsl:element>
</div>
</xsl:for-each>
</td>
<td>
<xsl:for-each select="/plugins/pyqgis_plugin">
<div class="plugin">
<div class="head">
<!--
<xsl:element name="a">
<xsl:attribute name="href">
<xsl:value-of select="homepage" />
</xsl:attribute>
-->
<xsl:value-of select="@name" /> : <xsl:value-of select="@version" />
<!--
</xsl:element>
-->
</div>
<div class="description">
<xsl:value-of select="description" />
</div>
<div class="download">
Download:
<xsl:element name="a">
 <xsl:attribute name="href">
  <xsl:value-of select="download_url" />
 </xsl:attribute>
 <xsl:value-of select="file_name" />
</xsl:element>
</div>
<div class="author">
Author: <xsl:value-of select="author_name" />
</div>
<div class="author">
Version: <xsl:value-of select="version" />
</div>
<div class="author">
Minimum QGIS Version: <xsl:value-of select="qgis_minimum_version" />
</div>
<div class="author">
Home page:
<xsl:element name="a">
 <xsl:attribute name="href">
  <xsl:value-of select="homepage" />
 </xsl:attribute>
 <xsl:value-of select="homepage" />
</xsl:element>
</div>
</div>
</xsl:for-each>
</td>
</tr>
</table>
<!--
<p>This URL is subject to change at release of QGIS 1.0
-->
</body>
</html>

</xsl:template>

</xsl:stylesheet>