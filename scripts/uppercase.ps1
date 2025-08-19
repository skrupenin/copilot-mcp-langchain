param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$InputText
)

# Convert text to uppercase
$UppercaseText = $InputText.ToUpper()

# Output the result
Write-Output $UppercaseText
