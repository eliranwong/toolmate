from toolmate import config

# @get_location @show_connection @start_recording @stop_recording
if config.isTermux:
    config.aliases["@get_location "] = "@command termux-location "
    config.aliases["@show_connection "] = "@command termux-wifi-connectioninfo "
    config.aliases["@start_recording "] = "@command termux-microphone-record -d "
    config.aliases["@stop_recording "] = "@command termux-microphone-record -q "

    config.inputSuggestions += ["@get_location ", "@show_connection ", "@start_recording ", "@stop_recording "]