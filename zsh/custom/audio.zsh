#!/usr/bin/env zsh

fix-audio() {
  # This fixes issues with audio crackling and missing devices.
  systemctl --user restart pipewire.service pipewire-pulse.service
  # For old PulseAudio
  # pulseaudio -k
  # sudo alsa force-reload
}

pipewire_id() {
  # https://gitlab.freedesktop.org/pipewire/wireplumber/-/issues/395#note_2007623
  pw-cli i "${1}" | grep --only-matching --perl-regexp "id: \K\w+"
}

audioconf() {
  # Audio configuration script for PipeWire
  # You can find the node names with:
  # pw-cli i all | grep "node.name"
  local COMBINED="combined"
  # If the correct profile is not available,
  # try connecting the transmitter directly to the computer instead of through a USB hub.
  # Somehow, this makes the correct profile available.
  local HEADPHONES="alsa_output.usb-SteelSeries_Arctis_Pro_Wireless-00.stereo-game"
  local HEADPHONES_MIC="alsa_input.usb-SteelSeries_Arctis_Pro_Wireless-00.mono-chat"
  local T480_SPEAKERS="alsa_output.pci-0000_00_1f.3.3.analog-stereo"
  local TB4_DOCK_ANALOG="alsa_output.usb-Lenovo_ThinkPad_Thunderbolt_4_Dock_USB_Audio_000000000000-00.3.analog-stereo"
  local WEBCAM="alsa_input.usb-046d_0821_A7E23B90-00.analog-stereo"
  local Z2E_HDMI="alsa_output.pci-0000_01_00.1.hdmi-surround-extra1.2"
  local Z2E_OPTICAL="alsa_output.usb-Generic_USB_Audio-00.2.iec958-ac3-surround-51"
  local Z2E_SPEAKERS="alsa_output.usb-Generic_USB_Audio-00.analog-surround-51"
  local Z2E_SPEAKERS2="alsa_output.usb-Generic_USB_Audio-00.2.analog-surround-51"

  local DEV_ID
  local NODES
  NODES="$(pw-cli i all | grep "node.name")"

  case "${1}" in
    all)
      if grep -q "${COMBINED}" <<< "${NODES}"; then
        DEV_ID="$(pipewire_id "${COMBINED}")"
        wpctl set-default "${DEV_ID}"
        wpctl set-volume "${DEV_ID}" 1
      else
        echo "Combined sink was not found. Have you loaded the user startup script?"
      fi
      ;;
    hdmi | HDMI)
      if grep -q "${Z2E_HDMI}" <<< "${NODES}"; then
        DEV_ID="$(pipewire_id "${Z2E_HDMI}")"
        wpctl set-default "${DEV_ID}"
        wpctl set-volume "${DEV_ID}" 1
      else
        echo "HDMI device was not found."
      fi
      ;;
    headphones)
      if grep -q "${HEADPHONES}" <<< "${NODES}"; then
        DEV_ID="$(pipewire_id "${HEADPHONES}")"
        wpctl set-default "${DEV_ID}"
        wpctl set-volume "${DEV_ID}" 1
      else
        echo "Headphones device was not found."
      fi
      if grep -q "${HEADPHONES_MIC}" <<< "${NODES}"; then
        DEV_ID="$(pipewire_id "${HEADPHONES_MIC}")"
        wpctl set-default "${DEV_ID}"
        wpctl set-volume "${DEV_ID}" 1
      else
        echo "Headphones mic device was not found."
      fi
      ;;
    optical | iec958 | IEC958)
      if grep -q "${COMBINED}" <<< "${NODES}"; then
        DEV_ID="$(pipewire_id "${Z2E_OPTICAL}")"
        wpctl set-default "${DEV_ID}"
        wpctl set-volume "${DEV_ID}" 1
      else
        echo "Optical device was not found."
      fi
      ;;
    speakers)
      if grep -q "${Z2E_SPEAKERS}" <<< "${NODES}"; then
        DEV_ID="$(pipewire_id "${Z2E_SPEAKERS}")"
        wpctl set-default "${DEV_ID}"
        wpctl set-volume "${DEV_ID}" 1
      elif grep -q "${Z2E_SPEAKERS2}" <<< "${NODES}"; then
        DEV_ID="$(pipewire_id "${Z2E_SPEAKERS2}")"
        wpctl set-default "${DEV_ID}"
        wpctl set-volume "${DEV_ID}" 1
      elif grep -q "${T480_SPEAKERS}" <<< "${NODES}"; then
        wpctl set-default "$(pipewire_id "${T480_SPEAKERS}")"
      else
        echo "Speaker device was not found."
      fi
      ;;
    tb4 | TB4)
      if grep -q "${HDMI_CARD}" <<< "${NODES}"; then
        wpctl set-default "$(pipewire_id "${TB4_DOCK_ANALOG}")"
      else
        echo "Thunderbolt dock was not found."
      fi
      ;;
    webcam | C910)
      if grep -q "${WEBCAM}" <<< "${NODES}"; then
        DEV_ID="$(pipewire_id "${WEBCAM}")"
        wpctl set-default "${DEV_ID}"
        wpctl set-volume "${DEV_ID}" 1
      else
        echo "Webcam mic was not found."
      fi
      ;;
    *)
      echo "Unknown device node name"
      ;;
  esac
}

audioconf_pulseaudio() {
  # Audio device configuration script for old PulseAudio
  # https://askubuntu.com/a/14083/
  local COMBINED_SINK="combined"
  local HDMI_CARD="alsa_card.pci-0000_03_00.1"
  local HDMI_PROFILE="output:hdmi-stereo"
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
      echo "Unknown config name"
      ;;
  esac
}
