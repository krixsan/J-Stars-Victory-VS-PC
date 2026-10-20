// SPDX-License-Identifier: GPL-2.0-or-later
// The launcher's view of the connected controllers, through the game's own SDL3 (bin\SDL3.dll,
// loaded at run time: the launcher stays one static .exe). The names, GUIDs and button names are
// the ones src/runtime_pad.c matches, so what is chosen here is what the game uses.
//
// Everything runs on the launcher's UI thread. Stop() closes every controller and SDL's gamepad
// subsystem before the game starts, so the game has the controllers to itself.

#pragma once

#include <cstdint>
#include <string>
#include <vector>

namespace Pads {

// SDL_GamepadButton order (static_assert'ed in gamepads.cpp).
enum Button {
    BtnSouth, BtnEast, BtnWest, BtnNorth, BtnBack, BtnGuide, BtnStart, BtnLeftStick, BtnRightStick, BtnLeftShoulder,
    BtnRightShoulder, BtnDpadUp, BtnDpadDown, BtnDpadLeft, BtnDpadRight, BtnMisc1, BtnRightPaddle1, BtnLeftPaddle1,
    BtnRightPaddle2, BtnLeftPaddle2, BtnTouchpad, BtnMisc2, BtnMisc3, BtnMisc4, BtnMisc5, BtnMisc6, BtnButtonCount,
    // Not SDL buttons: the triggers, as runtime_pad.c binds them (pad.l2=lefttrigger).
    BtnLeftTrigger = BtnButtonCount, BtnRightTrigger, BtnInputCount
};
// SDL_GamepadAxis order.
enum Axis { AxLeftX, AxLeftY, AxRightX, AxRightY, AxTriggerLeft, AxTriggerRight, AxAxisCount };

// The controller family: decides the buttons' labels and the drawing.
enum class Family { Xbox, PlayStation, Nintendo, Other };

struct Info {
    uint32_t id = 0;          // SDL_JoystickID (for this launcher session)
    std::string name, guid;   // as runtime_pad.c and the in-game menu see them
    int type = 0;             // SDL_GamepadType
    Family family = Family::Other;
    int battery = -1;         // percent, -1 unknown
    bool wireless = false, wired = false, charging = false;
};

struct State {
    bool buttons[BtnInputCount]{};  // triggers as pressed past half travel
    int16_t axes[AxAxisCount]{};
};

/// Loads bin\SDL3.dll and starts SDL's gamepad subsystem (once; again after Stop()). False with
/// Error() set when it cannot.
bool Start(const std::wstring& dll);
void Stop();
bool Running();
const std::string& Error();

/// Once per frame: polls the controllers and refreshes the list twice a second.
void Update();
const std::vector<Info>& List();
/// The live input of a controller in List(); false when it is gone.
bool Read(uint32_t id, State& out);
bool Rumble(uint32_t id, int ms);

/// Waits for the next press of a button or trigger on any controller (buttons held when this
/// is called do not count). TakeCapture() returns its runtime name ("a", "lefttrigger"...) and
/// the controller it came from, once.
void ArmCapture();
void CancelCapture();
bool Capturing();
bool TakeCapture(std::string& name, uint32_t& id);

/// The runtime/SDL name of a button ("a", "leftshoulder", "lefttrigger"); "" for none.
const char* InputName(int input);
/// The input of a runtime/SDL name, -1 when unknown.
int InputFromName(const std::string& name);
/// How a button is printed on a controller of this family (and type): "A", "Cruz", "LB", "ZL"...
std::string Label(int input, Family family, int type, bool spanish);
/// "Xbox One / Series", "DualSense (PS5)"...
std::string TypeName(int type, bool spanish);
Family FamilyOf(int type);

}  // namespace Pads
