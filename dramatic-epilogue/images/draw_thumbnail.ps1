Add-Type -AssemblyName System.Drawing
$width = 1200
$height = 630
$bmp = New-Object System.Drawing.Bitmap $width, $height
$graphics = [System.Drawing.Graphics]::FromImage($bmp)
$graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAlias
$graphics.Clear([System.Drawing.Color]::FromArgb(255, 10, 10, 15))

$brushGlow = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(40, 29, 185, 84))
$graphics.FillEllipse($brushGlow, 300, -100, 600, 600)

$fontTitle = New-Object System.Drawing.Font('Malgun Gothic', 100, [System.Drawing.FontStyle]::Bold)
$fontSub = New-Object System.Drawing.Font('Malgun Gothic', 40, [System.Drawing.FontStyle]::Regular)
$brushWhite = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
$brushGreen = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 29, 185, 84))

$format = New-Object System.Drawing.StringFormat
$format.Alignment = [System.Drawing.StringAlignment]::Center

$graphics.DrawString('드라마틱 에필로그', $fontTitle, $brushWhite, 600.0, 150.0, $format)
$graphics.DrawString('Ep. 이제부터 베드로', $fontSub, $brushGreen, 600.0, 360.0, $format)

$bmp.Save('og-cover.jpg', [System.Drawing.Imaging.ImageFormat]::Jpeg)

$graphics.Dispose()
$bmp.Dispose()
