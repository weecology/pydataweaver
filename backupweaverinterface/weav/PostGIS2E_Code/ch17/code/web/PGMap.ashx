<%@ WebHandler Language="VB" Class="PGMap" %>
Imports System
Imports System.Web
Imports Npgsql
Public Class PGMap : Implements IHttpHandler

     Public Sub ProcessRequest(ByVal context As HttpContext) Implements IHttpHandler.ProcessRequest
        Dim command As NpgsqlCommand
        
        'Dim nParam As NpgsqlParameter = New Npgsql.NpgsqlParameter(
        Dim sql As String
        Using conn As NpgsqlConnection = New NpgsqlConnection(System.Configuration.ConfigurationManager.ConnectionStrings("PGDSN").ConnectionString)
            conn.Open()
           
            sql = "SELECT ch17.get_rast_tile(:param_format, :param_width, :param_height, :param_srid, :param_bbox, :param_schema, :param_table) "
        

            command = New NpgsqlCommand(sql, conn)
            
            command.Parameters.Add(New NpgsqlParameter("param_format", context.Request("format").ToString()))
            command.Parameters.Add(New NpgsqlParameter("param_width", context.Request("WIDTH").ToString()))
            command.Parameters.Add(New NpgsqlParameter("param_height", context.Request("HEIGHT").ToString()))
            If context.Request("VERSION") = "1.1.1" Then
                command.Parameters.Add(New NpgsqlParameter("param_srid", context.Request("SRS").ToString().Replace("EPSG:", "")))
            Else 'assume 1.3.0
                command.Parameters.Add(New NpgsqlParameter("param_srid", context.Request("CRS").ToString().Replace("EPSG:", "")))
            End If
            
            command.Parameters.Add(New NpgsqlParameter("param_bbox", context.Request("BBOX").ToString()))
            command.Parameters.Add(New NpgsqlParameter("param_schema", context.Request("SCHEMA").ToString()))
            command.Parameters.Add(New NpgsqlParameter("param_table", context.Request("LAYERS").ToString()))
           

            Try
                context.Response.ContentType = context.Request("FORMAT")
                context.Response.BinaryWrite(command.ExecuteScalar())
            Catch ex As Exception
                context.Response.ContentType = "html/text"
                context.Response.Write(ex.Message.Trim)
            End Try
            conn.Close()

        End Using
    End Sub

    Public ReadOnly Property IsReusable() As Boolean Implements IHttpHandler.IsReusable
        Get
            Return True
        End Get
    End Property
End Class

