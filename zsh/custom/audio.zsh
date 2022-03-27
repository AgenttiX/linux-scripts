#!/usr/bin/env zsh

audioconf() {
  # https://askubuntu.com/a/14083/
  local COMBINED_SINK="combined"
  local HDMI_CARD="alsa_card.pci-0000_03_00.1"
  local HDMI_PROFILE="output:hdmi-surround"
  local HDMI_SINK="alsa_output.pci-0000_03_00.1.hdmi-surround"
  local HEADPHONE_CARD="alsa_card.usb-SteelSeries_Arctis_Pro_Wireless-00"
  local HEADPHONE_PROFILE="output:mono-chat+output:stereo-game+input:mono-chat"
  local HEADPHONE_SINK="alsa_output.usb-SteelSeries_Arctis_Pro_Wireless-00.stereo-game"
  local HEADPHONE_MIC="alsa_input.usb-SteelSeries_Arctis_Pro_Wireless-00.mono-chat"
  # TODO: fix the speaker port settings
  local SPEAKER_CARD="alsa_card.usb-Generic_USB_Audio-00"
  local SPEAKER_PROFILE="output:analog-stereo+input:analog-stereo"
  local SPEAKER_SINK="alsa_output.usb-Generic_USB_Audio-00.analog-stereo"

  case "${1}" in
    all)
      # https://stackoverflow.com/a/31195882/
      if pacmd list-sinks | grep -q "${COMBINED_SINK}"; then
        pacmd set-default-sink "${COMBINED_SINK}"
        # This could cause problems with USB headphones that don't have their own volume control.
        # pacmd set-sink-volume "${COMBINED_SINK}" 65536
      else
        echo "Combined sink was not found."
      fi
      ;;
    hdmi | HDMI)
      if pacmd list-cards | grep -q "${HDMI_CARD}"; then
        pacmd set-card-profile "${HDMI_CARD}" "${HDMI_PROFILE}"
      else
        echo "GPU card was not found."
      fi
      if pacmd list-sinks | grep -q "${HDMI_SINK}"; then
        pacmd set-default-sink "${HDMI_SINK}"
        pacmd set-sink-volume "${HDMI_SINK}" 65536
      else
        echo "GPU sink was not found."
      fi
      ;;
    headphones)
      if pacmd list-cards | grep -q "${HEADPHONE_CARD}"; then
        pacmd set-card-profile "${HEADPHONE_CARD}" "${HEADPHONE_PROFILE}"
      else
        echo "Headphone card was not found."
      fi
      if pacmd list-sinks | grep -q "${HEADPHONE_SINK}"; then
        pacmd set-default-sink "${HEADPHONE_SINK}"
        pacmd set-sink-volume "${HEADPHONE_SINK}" 65536
      else
        echo "Headphone sink was not found."
      fi
      if pacmd list-sources | grep -q "${HEADPHONE_MIC}"; then
        pacmd set-default-source "${HEADPHONE_MIC}"
        pacmd set-source-volume "${HEADPHONE_MIC}" 65536
      else
        echo "Headphone mic was not found."
      fi
      ;;
    speakers)
      if pacmd list-cards | grep -q "${SPEAKER_CARD}"; then
        pacmd set-card-profile "${SPEAKER_CARD}" "${SPEAKER_PROFILE}"
      else
        echo "Speaker card was not found."
      fi
      if pacmd list-sinks | grep -q "${SPEAKER_SINK}"; then
        pacmd set-default-sink "${SPEAKER_SINK}"
        pacmd set-sink-volume "${SPEAKER_SINK}" 65536
      else
        echo "Speaker sink was not found."
      fi
      ;;
    usb-c | USB-c)
      echo "Not yet implemented"
      ;;
    *)
      echo -n "Unknown config name"
      ;;
  esac
}
