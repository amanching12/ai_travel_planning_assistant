$base = "http://127.0.0.1:8000/chat"

$questions = @(
    "What are the must-visit attractions in Singapore?",
    "What is the weather in Singapore for the next three days?",
    "Convert INR 60000 to SGD and suggest a three-day itinerary.",
    "Create a three-day Singapore itinerary for next week and adjust it according to the weather forecast."
)

$session = $null
foreach ($q in $questions) {
    $body = @{ message = $q; session_id = $session } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri $base -Method Post -ContentType "application/json" -Body $body
    $session = $response.session_id
    "`nQUESTION: $q"
    "MODE: $($response.mode)"
    "ANSWER:`n$($response.answer)"
}
