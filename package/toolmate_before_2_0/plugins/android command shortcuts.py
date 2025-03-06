from toolmate import config

# @show_location @show_connection @start_recording @stop_recording
if config.isTermux:
    config.aliases["@show_location "] = "@command termux-location "
    config.aliases["@show_connection "] = "@command termux-wifi-connectioninfo "
    config.aliases["@start_recording "] = "@command termux-microphone-record -d "
    config.aliases["@stop_recording "] = "@command termux-microphone-record -q "

    config.builtinTools["show_location"] = "show location"
    config.builtinTools["show_connection"] = "show connection"
    config.builtinTools["start_recording"] = "start recording"
    config.builtinTools["stop_recording"] = "stop recording"

    config.inputSuggestions += ["@show_location ", "@show_connection ", "@start_recording ", "@stop_recording "]