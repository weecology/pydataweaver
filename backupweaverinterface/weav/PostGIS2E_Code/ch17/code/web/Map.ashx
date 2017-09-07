<%@ WebHandler Language="VB" Class="GetPAMap" %>
Imports System
Imports System.Web

Public Class GetPAMap : Implements IHttpHandler
    Public Sub ProcessRequest(ByVal context As HttpContext) Implements IHttpHandler.ProcessRequest
        Dim mapURLStub As String = "http://" + context.Request.ServerVariables("HTTP_HOST") + "/mapserv/mapserv.exe?map="
        Dim mapfile As String = "C:/mapserv/chapter_17/postgis_in_action.map"
        Dim WebRequestObject As System.Net.HttpWebRequest
        Dim sr As System.IO.StreamReader
        Dim WebResponseObject As System.Net.HttpWebResponse
        Dim sb As New System.Text.StringBuilder()
        Dim key As String
        sb.Append(mapURLStub + mapfile) 	
        Try
			For Each key In context.Request.QueryString.AllKeys
				sb.Append("&" + key + "=" + context.Server.UrlEncode(context.Request.QueryString(key)))            
			Next
            WebRequestObject = DirectCast(System.Net.WebRequest.Create(sb.ToString()), System.Net.HttpWebRequest)
            WebRequestObject.Method = "GET"
            WebResponseObject = DirectCast(WebRequestObject.GetResponse(), System.Net.HttpWebResponse)
            If context.Request("REQUEST").ToString.ToLower() = "getcapabilities" _
		orElse context.Request("REQUEST").ToString.ToLower() = "getfeatureinfo" Then 
	     		sr = New System.IO.StreamReader(WebResponseObject.GetResponseStream)
                context.Response.ContentType = "application/xml"
                context.Response.Write(sr.ReadToEnd())
            Else 'assume an image is being returned
                context.Response.ContentType = context.Request("format").ToString()
				Dim outs As System.IO.Stream = WebRequestObject.GetResponse().GetResponseStream()
				Dim buffer As Byte() = New Byte(&H1000) {}
				Dim read As Integer
				read = outs.Read(buffer, 0, buffer.Length)
				While (read > 0)
				  context.Response.OutputStream.Write(buffer, 0, read)
				  read = outs.Read(buffer, 0, buffer.Length)
				End While
            End If
           
            Try
                WebResponseObject.Close()
                WebRequestObject.Abort()
            Catch
             
            End Try

        Catch Ex As Exception 'assume it fails here if the web request fails
            context.Response.ContentType = "text/xml"
            context.Response.Write(Ex.ToString())
        End Try
    End Sub

    Public ReadOnly Property IsReusable() As Boolean Implements IHttpHandler.IsReusable
        Get
            Return True
        End Get
    End Property
End Class

