/* ============================================================================
 *  PORTFOLIO CONTENT  —  THIS IS THE ONLY FILE YOU NEED TO EDIT
 * ----------------------------------------------------------------------------
 *  To add a project: copy one { ... } block inside the `projects: [ ]` array,
 *  paste it, and change the fields. To edit your bio/links, change `profile`.
 *  See README.md for the full how-to. Nothing else needs to change.
 * ========================================================================== */

window.PORTFOLIO = {

  /* ----- Your info (shown in the hero, about, and footer) ----------------- */
  profile: {
    name: "Will Mattis",
    role: "Electrical & Computer Engineer",
    // One punchy line under your name on the homepage:
    tagline: "Embedded systems & PCB design for high-voltage EV powertrains.",
    location: "Cincinnati, OH",
    email: "willmattis86@gmail.com",

    // A short paragraph for the About section. Edit freely.
    about: "Electrical engineering student at the University of Cincinnati and a " +
      "member of Bearcats Electric Racing, where I design and build the electronics " +
      "behind a Formula-style electric race car. My work spans the full battery " +
      "management system — from cell-level sensing boards to the high-voltage " +
      "safety hardware and the master controller that ties it all together. I enjoy " +
      "taking a system from schematic capture and PCB layout through bring-up, " +
      "firmware, and on-car validation.",

    // Links shown as buttons. Delete a line to hide that button.
    // Leave the value as "" to hide it too.
    links: {
      email: "willmattis86@gmail.com",
      linkedin: "",          // e.g. "https://www.linkedin.com/in/yourname"
      github: "",            // e.g. "https://github.com/yourname"
      resume: ""             // e.g. "assets/files/resume.pdf"
    },

    // Skill chips shown in the About section.
    skills: [
      "Altium Designer", "Schematic Capture", "PCB Layout", "LTspice",
      "Embedded C / C++", "Teensy / Arduino", "CAN Bus", "isoSPI",
      "Battery Management (BMS)", "High-Voltage Safety", "Soldering & Rework",
      "Hardware Bring-up", "Oscilloscope / DMM"
    ]
  },

  /* ----- Section order on the homepage ------------------------------------ *
   *  Projects are grouped into sections by their `group` field. List the
   *  groups here in the order you want them to appear. Each has an optional
   *  one-line `blurb`. A project whose `group` isn't listed here still shows
   *  up — it just lands in a catch-all section at the bottom.
   * ----------------------------------------------------------------------- */
  groups: [
    { name: "Bearcats Electric Racing", blurb: "Battery-management and high-voltage electronics for a Formula-style electric race car." },
    { name: "X-Inator",                 blurb: "My startup — hardware I'm designing and building from the ground up." },
    { name: "School Projects",          blurb: "Coursework and academic engineering projects at the University of Cincinnati." }
  ],

  /* ----- Projects --------------------------------------------------------- *
   *  Each project supports these fields:
   *    slug        (required) unique id, lowercase-with-dashes — used in the URL
   *    title       (required) project name
   *    subtitle    short one-liner under the title
   *    org         team / company / context (e.g. "Bearcats Electric Racing")
   *    date        any string, e.g. "2026" or "Spring 2026"
   *    status      e.g. "Shipped", "In testing", "Prototype" (optional badge)
   *    tags        array of short keywords (shown as chips)
   *    thumb       card image (path under assets/img/ or a full URL)
   *    summary     1–3 sentences shown on the card and at the top of the page
   *    role        YOUR contribution — EDIT THIS to match what you did
   *    highlights  array of bullet points (the headline achievements)
   *    sections    array of { heading, body } — the long-form write-up
   *    specs       array of { label, value } — quick technical facts table
   *    gallery     array of { src, caption } images (optional)
   *    files       array of { label, href, kind } downloads (pdf/step/file)
   *    links       array of { label, href } external links (optional)
   * ----------------------------------------------------------------------- */
  projects: [

    {
      slug: "bms-sense-board",
      title: "BMS Sense Board",
      subtitle: "16-cell voltage & 10-channel temperature monitor",
      org: "Bearcats Electric Racing",
      group: "Bearcats Electric Racing",
      date: "2026",
      status: "Bring-up",
      tags: ["Altium", "BMS", "ADBMS6830", "isoSPI", "Mixed-signal"],
      thumb: "assets/img/card-bms-sense.svg",
      model: "assets/files/bms-sense.step",
      summary: "Cell-monitoring board for the accumulator that measures every series " +
        "cell voltage and ten pack temperatures, reporting back to the master over an " +
        "isolated isoSPI daisy chain.",
      role: "I worked on the schematic capture and PCB layout for this board, " +
        "including the cell-tap filtering and the isoSPI communication front-end. " +
        "// EDIT this line to describe exactly what you did.",
      highlights: [
        "Built around the Analog Devices ADBMS6830 multicell battery-stack monitor",
        "Monitors 16 series cell voltages with per-cell passive balancing taps",
        "10 NTC temperature channels routed through the monitor's GPIO/mux",
        "Isolated isoSPI (SPI_A / SPI_B differential pairs) for noise-immune, " +
          "daisy-chainable communication up the high-voltage stack"
      ],
      sections: [
        {
          heading: "Overview",
          body: "The sense board is the front-line measurement node of the battery " +
            "management system. One board sits on each segment of the accumulator and " +
            "continuously samples individual cell voltages and pack temperatures, then " +
            "streams that data to the master controller. Because it lives at high " +
            "potential, all communication is galvanically isolated."
        },
        {
          heading: "Measurement front-end",
          body: "Each cell tap (S1–S16) is filtered before reaching the ADBMS6830 to " +
            "reject switching noise from the rest of the car. Temperature is read through " +
            "ten NTC channels tied to the monitor's auxiliary inputs, giving good thermal " +
            "coverage across the segment. Precision references (VREF1/VREF2) anchor the " +
            "voltage measurements."
        },
        {
          heading: "Isolated communication",
          body: "Boards talk to the master over isoSPI — a differential, transformer- " +
            "isolated SPI variant — using the A and B differential pairs so multiple " +
            "sense boards can be daisy-chained up the series stack without a separate " +
            "isolator per board."
        }
      ],
      specs: [
        { label: "Monitor IC", value: "Analog Devices ADBMS6830BCSWZ" },
        { label: "Cell channels", value: "16 series cells" },
        { label: "Temp channels", value: "10 (NTC)" },
        { label: "Comms", value: "Isolated isoSPI (daisy-chain)" },
        { label: "Tool", value: "Altium Designer" }
      ],
      gallery: [
        { src: "assets/img/bms-sense-schematic.png", caption: "Schematic — ADBMS6830 cell & temperature monitoring front-end" }
      ],
      files: [
        { label: "Schematic (PDF)", href: "assets/files/bms-sense-schematic.pdf", kind: "pdf" },
        { label: "3D model (STEP)", href: "assets/files/bms-sense.step", kind: "step" }
      ],
      links: []
    },

    {
      slug: "bms-main-master",
      title: "BMS Main — Master Controller",
      subtitle: "Teensy 4.1 master ECU for the battery management system",
      org: "Bearcats Electric Racing",
      group: "Bearcats Electric Racing",
      date: "2026",
      status: "Bring-up",
      tags: ["Altium", "Teensy 4.1", "CAN", "isoSPI", "Embedded"],
      thumb: "assets/img/card-bms-main.svg",
      model: "assets/files/bms-main.step",
      summary: "The brain of the BMS: a Teensy 4.1–based controller that gathers data " +
        "from the sense boards over isoSPI, measures pack current, and drives the car's " +
        "shutdown, charging, and cooling outputs while talking to the vehicle over CAN.",
      role: "I worked on this master board — integrating the Teensy with the isoSPI " +
        "front-end, CAN interface, and output drivers. " +
        "// EDIT this line to describe exactly what you did.",
      highlights: [
        "Teensy 4.1 (DEV-16996) master microcontroller",
        "isoSPI front-end to communicate with the daisy-chained sense boards",
        "Hall-effect current sensing for pack current and BSPD",
        "CAN bus interface to the rest of the vehicle (CANH / CANL)",
        "Drives shutdown-circuit, charger-enable, cooling, and switch outputs",
        "Onboard fuse / shunt provisions and HV/VI temperature inputs"
      ],
      sections: [
        {
          heading: "Overview",
          body: "The master board is the central controller of the battery management " +
            "system. It aggregates per-cell and per-temperature data from every sense " +
            "board, evaluates the safety state of the pack, and is the single point that " +
            "commands the high-voltage contactors, charger, and cooling system."
        },
        {
          heading: "Sensing & communication",
          body: "An isoSPI interface (BMS_isoSPI) connects the master to the isolated " +
            "sense-board chain, while a Hall-effect current sensor provides pack current " +
            "and feeds the brake-system-plausibility (BSPD) logic. A dedicated CAN " +
            "transceiver (BMS_CAN) puts pack telemetry and faults onto the vehicle bus."
        },
        {
          heading: "Outputs & safety",
          body: "The output stage (BMS_Outputs) drives the shutdown circuit, charger " +
            "enable, cooling, and a switched output. Fuse footprints — populated with " +
            "0 Ω links unless needed — keep the safety options open during development."
        }
      ],
      specs: [
        { label: "Controller", value: "Teensy 4.1 (DEV-16996)" },
        { label: "Cell comms", value: "Isolated isoSPI" },
        { label: "Current sense", value: "Hall-effect + BSPD" },
        { label: "Vehicle comms", value: "CAN (CANH / CANL)" },
        { label: "Outputs", value: "Shutdown · Charger · Cooling · Switch" },
        { label: "Tool", value: "Altium Designer" }
      ],
      gallery: [
        { src: "assets/img/bms-main-schematic.png", caption: "Schematic — Teensy 4.1 master with isoSPI, CAN, Hall sensing, and output drivers" }
      ],
      files: [
        { label: "Schematic (PDF)", href: "assets/files/bms-main-schematic.pdf", kind: "pdf" },
        { label: "3D model (STEP)", href: "assets/files/bms-main.step", kind: "step" },
        { label: "Buck-converter LTspice sim (.asc)", href: "assets/files/bms-main-buck.asc", kind: "file" }
      ],
      links: []
    },

    {
      slug: "hv-sense-board",
      title: "HV Sense Board",
      subtitle: "Isolated high-voltage sensing, precharge & AIR control",
      org: "Bearcats Electric Racing",
      group: "Bearcats Electric Racing",
      date: "2026",
      status: "Bring-up",
      tags: ["Altium", "High-Voltage", "Isolation", "Precharge", "Safety"],
      thumb: "assets/img/card-hv-sense.svg",
      model: "assets/files/hv-sense.step",
      summary: "Safety-critical board that measures the high-voltage bus across an " +
        "isolation barrier, detects a completed precharge, and switches the Accumulator " +
        "Isolation Relays (AIRs) through opto-isolated MOSFET drivers.",
      role: "I worked on the high-voltage measurement chain and the isolated relay-drive " +
        "circuitry on this board. " +
        "// EDIT this line to describe exactly what you did.",
      highlights: [
        "High-voltage measurement via high-value precision resistor dividers",
        "LM211 comparators detect HV presence and precharge-complete",
        "Galvanic isolation (ISO7720D digital isolator + isolated DC-DC converters)",
        "Opto-isolated (TLP240A) MOSFET drivers switch AIR_1 / AIR_2 contactors",
        "Dedicated precharge resistor network with current-limited charge path",
        "Isolated HV temperature sensing back to the low-voltage domain"
      ],
      sections: [
        {
          heading: "Overview",
          body: "The HV sense board enforces the boundary between the tractive (high- " +
            "voltage) system and the low-voltage control electronics. Everything on the " +
            "board is split into HV and LV domains separated by a galvanic isolation " +
            "barrier, so the controller can safely 'see' the high-voltage bus and command " +
            "the contactors without any direct electrical connection."
        },
        {
          heading: "Voltage sensing & precharge",
          body: "The tractive-system voltage is scaled down through chains of high-voltage " +
            "precision divider resistors and compared with LM211 comparators to generate " +
            "'HV present' and 'precharge finished' signals. A dedicated precharge resistor " +
            "network limits inrush current while the DC bus capacitance charges before the " +
            "main contactors close."
        },
        {
          heading: "Isolation & relay drive",
          body: "Isolated DC-DC converters and an ISO7720D digital isolator carry power " +
            "and signals across the barrier. On the high side, TLP240A photovoltaic " +
            "drivers switch SQ2318 MOSFETs to energize the Accumulator Isolation Relays " +
            "(AIR_1, AIR_2) only when the Accumulator-Enable condition is satisfied."
        }
      ],
      specs: [
        { label: "Function", value: "HV sense · precharge detect · AIR control" },
        { label: "Comparators", value: "LM211 (HV present / precharge done)" },
        { label: "Isolation", value: "ISO7720D + isolated DC-DC" },
        { label: "Relay drive", value: "TLP240A opto → SQ2318 MOSFET" },
        { label: "Domains", value: "HV / LV split with galvanic barrier" },
        { label: "Tool", value: "Altium Designer" }
      ],
      gallery: [
        { src: "assets/img/hv-sense-schematic.png", caption: "Schematic — HV/LV split with divider sensing, precharge, and isolated AIR drivers" }
      ],
      files: [
        { label: "Schematic (PDF)", href: "assets/files/hv-sense-schematic.pdf", kind: "pdf" },
        { label: "3D model (STEP)", href: "assets/files/hv-sense.step", kind: "step" },
        { label: "Temp / frequency data (XLSX)", href: "assets/files/hv-sense-temp-frequency.xlsx", kind: "file" }
      ],
      links: []
    },

    {
      slug: "can-hat",
      title: "CAN Hat",
      subtitle: "Raspberry Pi CAN interface board",
      org: "Bearcats Electric Racing",
      group: "Bearcats Electric Racing",
      date: "2026",
      status: "Built",
      tags: ["Altium", "CAN", "MCP2515", "Raspberry Pi"],
      thumb: "assets/img/card-can-hat.svg",
      model: "assets/files/can-hat.step",
      summary: "A 40-pin Raspberry Pi HAT that adds an isolated CAN interface, letting a " +
        "Pi log and interact with the car's CAN bus for data acquisition and debugging.",
      role: "I worked on the schematic and layout of this CAN HAT, including the " +
        "controller, transceiver, and Pi header integration. " +
        "// EDIT this line to describe exactly what you did.",
      highlights: [
        "Standard 40-pin Raspberry Pi GPIO HAT form factor",
        "MCP2515 SPI CAN controller with a 16 MHz crystal",
        "TCAN337 CAN transceiver with bus protection and termination",
        "Lets a Raspberry Pi sniff, log, and transmit on the vehicle CAN bus"
      ],
      sections: [
        {
          heading: "Overview",
          body: "The CAN HAT turns a Raspberry Pi into a CAN node so the team can log " +
            "vehicle traffic and prototype higher-level tools against the same bus the BMS " +
            "and other ECUs use. It plugs straight onto the Pi's 40-pin header."
        },
        {
          heading: "How it works",
          body: "An MCP2515 controller handles the CAN protocol and talks to the Pi over " +
            "SPI, clocked by a 16 MHz crystal. A TCAN337 transceiver drives the physical " +
            "bus, with split termination and bus-protection components at the connector."
        }
      ],
      specs: [
        { label: "Form factor", value: "Raspberry Pi 40-pin HAT" },
        { label: "Controller", value: "MCP2515 (SPI)" },
        { label: "Transceiver", value: "TCAN337GDCNR" },
        { label: "Clock", value: "16 MHz crystal" },
        { label: "Tool", value: "Altium Designer" }
      ],
      gallery: [
        { src: "assets/img/can-hat-schematic.png", caption: "Schematic — MCP2515 controller and TCAN337 transceiver on a Pi HAT" }
      ],
      files: [
        { label: "Schematic (PDF)", href: "assets/files/can-hat-schematic.pdf", kind: "pdf" },
        { label: "3D model (STEP)", href: "assets/files/can-hat.step", kind: "step" }
      ],
      links: []
    },

    /* ===================== X-INATOR (STARTUP) ============================== */
    {
      slug: "x-inator-antechamber",
      title: "X-Inator — Antechamber Assembly",
      subtitle: "Mechanical assembly for my startup's hardware",
      org: "X-Inator",
      group: "X-Inator",
      date: "2026",
      status: "Prototype",
      tags: ["CAD", "Mechanical", "Startup", "Assembly"],
      thumb: "assets/img/xinator-0.jpg",
      model: "assets/files/x-inator-antechamber.step",
      summary: "An early hardware assembly for X-Inator, the startup I'm building. " +
        "// EDIT this summary to describe what X-Inator is and what this assembly does.",
      role: "I designed and built this assembly end to end. " +
        "// EDIT this line to describe exactly what you did.",
      highlights: [
        "// EDIT — add a headline achievement",
        "// EDIT — add another"
      ],
      sections: [
        { heading: "Overview", body: "// EDIT — describe X-Inator and the goal of this build." },
        { heading: "Design", body: "// EDIT — describe the mechanical design and decisions." }
      ],
      specs: [
        { label: "Type", value: "Mechanical assembly" },
        { label: "Tool", value: "// EDIT — e.g. SolidWorks / Fusion 360" }
      ],
      gallery: [
        { src: "assets/img/xinator-0.jpg", caption: "// EDIT caption" },
        { src: "assets/img/xinator-1.jpg", caption: "" },
        { src: "assets/img/xinator-2.jpg", caption: "" },
        { src: "assets/img/xinator-3.jpg", caption: "" },
        { src: "assets/img/xinator-4.jpg", caption: "" },
        { src: "assets/img/xinator-5.jpg", caption: "" },
        { src: "assets/img/xinator-6.jpg", caption: "" },
        { src: "assets/img/xinator-7.jpg", caption: "" }
      ],
      files: [
        { label: "3D model (STEP)", href: "assets/files/x-inator-antechamber.step", kind: "step" }
      ],
      links: []
    },

    /* ===================== SCHOOL PROJECTS ================================= */
    {
      slug: "dc-motor-assembly",
      title: "DC Motor Assembly",
      subtitle: "Designed and modeled DC motor build",
      org: "University of Cincinnati",
      group: "School Projects",
      date: "2026",
      status: "Built",
      tags: ["CAD", "Electromechanical", "DC Motor"],
      thumb: "assets/img/motor-1.jpg",
      model: "assets/files/dc-motor.step",
      summary: "A DC motor assembly designed and modeled for a school project. " +
        "// EDIT this summary to describe the assignment and what the motor does.",
      role: "// EDIT — describe exactly what you did on this project.",
      highlights: [
        "// EDIT — add a headline achievement",
        "// EDIT — add another"
      ],
      sections: [
        { heading: "Overview", body: "// EDIT — describe the project goal and context." },
        { heading: "Build", body: "// EDIT — describe how it was designed/built and what you learned." }
      ],
      specs: [
        { label: "Type", value: "DC motor assembly" },
        { label: "Tool", value: "// EDIT — e.g. SolidWorks / Fusion 360" }
      ],
      gallery: [
        { src: "assets/img/motor-1.jpg", caption: "// EDIT caption" },
        { src: "assets/img/motor-2.jpg", caption: "" }
      ],
      files: [
        { label: "3D model (STEP)", href: "assets/files/dc-motor.step", kind: "step" }
      ],
      links: []
    }

  ]
};
