#!/usr/bin/env zsh

audioconf() {
  # https://askubuntu.com/a/14083/
  local COMBINED_SINK="combined"
  local HDMI_CARD="alsa_card.pci-0000_03_00.1"
  HDMI_PROFILE="output:hdmi-stereo"
  # HDMI surround does not work yet with my current TV setup.
  # The front channels work with it, though, but the audio going to the back channels is dropped.
  # local HDMI_PROFILE="output:hdmi-surround"
  local HDMI_SINK="alsa_output.pci-0000_03_00.1.hdmi-stereo"
  # local HDMI_SINK="alsa_output.pci-0000_03_00.1.hdmi-surround"
  local HEADPHONE_CARD="alsa_card.usb-SteelSeries_Arctis_Pro_Wireless-00"
  local HEADPHONE_PROFILE="output:mono-chat+output:stereo-game+input:mono-chat"
  local HEADPHONE_SINK="alsa_output.usb-SteelSeries_Arctis_Pro_Wireless-00.stereo-game"
  local HEADPHONE_MIC="alsa_input.usb-SteelSeries_Arctis_Pro_Wireless-00.mono-chat"
  # TODO: fix the speaker port settings
  local SPEAKER_CARD="alsa_card.usb-Generic_USB_Audio-00"
  local SPEAKER_PROFILE="output:analog-stereo+input:analog-stereo"
  local SPEAKER_SINK="alsa_output.usb-Generic_USB_Audio-00.analog-stereo"
  local T480_CARD="alsa_card.pci-0000_00_1f.3"
  local T480_HDMI_PROFILE="output:hdmi-stereo-extra1+input:analog-stereo"
  local T480_HDMI_SINK="alsa_output.pci-0000_00_1f.3.hdmi-stereo-extra1"
  local T480_SPEAKER_PROFILE="${SPEAKER_PROFILE}"
  local T480_SPEAKER_SINK="alsa_output.pci-0000_00_1f.3.analog-stereo"
  local T480_THUNDERBOLT_PROFILE="output:hdmi-stereo+input:analog-stereo"
  local T480_THUNDERBOLT_SINK="alsa_output.pci-0000_00_1f.3.hdmi-stereo"
  local T480_USBC_PROFILE="output:hdmi-stereo-extra1+input:analog-stereo"
  local T480_USBC_SINK="alsa_output.pci-0000_00_1f.3.hdmi-stereo-extra1"

  local CARDS
  CARDS=$(pacmd list-cards)

  case "${1}" in
    all)
      # https://stackoverflow.com/a/31195882/
      if grep -q "${COMBINED_SINK}" <<< "${CARDS}"; then
        pacmd set-default-sink "${COMBINED_SINK}"
        # This could cause problems with USB headphones that don't have their own volume control.
        # pacmd set-sink-volume "${COMBINED_SINK}" 65536
      else
        echo "Combined sink was not found."
      fi
      ;;
    hdmi | HDMI)
      if grep -q "${HDMI_CARD}" <<< "${CARDS}"; then
        pacmd set-card-profile "${HDMI_CARD}" "${HDMI_PROFILE}"
        if pacmd list-sinks | grep -q "${HDMI_SINK}"; then
          pacmd set-default-sink "${HDMI_SINK}"
          pacmd set-sink-volume "${HDMI_SINK}" 65536
        else
          echo "HDMI sink was not found."
        fi
      elif pacmd list-cards | grep -q "${T480_CARD}"; then
        pacmd set-card-profile "${T480_CARD}" "${T480_HDMI_PROFILE}"
        if pacmd list-sinks | grep -q "${T480_HDMI_SINK}"; then
          pacmd set-default-sink "${T480_HDMI_SINK}"
          pacmd set-sink-volume "${T480_HDMI_SINK}" 65536
        else
          echo "HDMI sink was not found."
        fi
      else
        echo "HDMI card was not found."
      fi
      ;;
    headphones)
      if grep -q "${HEADPHONE_CARD}" <<< "${CARDS}"; then
        pacmd set-card-profile "${HEADPHONE_CARD}" "${HEADPHONE_PROFILE}"
        if grep -q "${HEADPHONE_SINK}" <<< "${CARDS}"; then
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
      else
        echo "Headphone card was not found."
      fi
      ;;
    speakers)
      if grep -q "${SPEAKER_CARD}" <<< "${CARDS}"; then
        pacmd set-card-profile "${SPEAKER_CARD}" "${SPEAKER_PROFILE}"
        if pacmd list-sinks | grep -q "${SPEAKER_SINK}"; then
          pacmd set-default-sink "${SPEAKER_SINK}"
          pacmd set-sink-volume "${SPEAKER_SINK}" 65536
        else
          echo "Speaker sink was not found."
        fi
      elif grep -q "${T480_CARD}" <<< "${CARDS}"; then
        pacmd set-card-profile "${T480_CARD}" "${T480_SPEAKER_PROFILE}"
        if pacmd list-sinks | grep -q "${T480_SPEAKER_SINK}"; then
          pacmd set-default-sink "${T480_SPEAKER_SINK}"
        else
          echo "Speaker sink was not found."
        fi
      else
        echo "Speaker card was not found."
      fi
      ;;
    thunderbolt | Thunderbolt | tb | TB)
      if grep -q "${T480_CARD}" <<< "${CARDS}"; then
        pacmd set-card-profile "${T480_CARD}" "${T480_THUNDERBOLT_PROFILE}"
        if pacmd list-sinks | grep -q "${T480_THUNDERBOLT_SINK}"; then
          pacmd set-default-sink "${T480_THUNDERBOLT_SINK}"
          pacmd set-sink-volume "${T480_THUNDERBOLT_SINK}" 65536
        else
          echo "Thunderbolt sink was not found."
        fi
      else
        echo "Thunderbolt card was not found."
      fi
      ;;
    usb-c | USB-c)
      if grep -q "${T480_CARD}" <<< "${CARDS}"; then
        pacmd set-card-profile "${T480_CARD}" "${T480_USBC_PROFILE}"
        if pacmd list-sinks | grep -q "${T480_USBC_SINK}"; then
          pacmd set-default-sink "${T480_USBC_SINK}"
          pacmd set-sink-volume "${T480_USBC_SINK}" 65536
        else
          echo "USB-c sink was not found."
        fi
      else
        echo "USB-c card was not found."
      fi
      ;;
    *)
      echo -n "Unknown config name"
      ;;
  esac
}
