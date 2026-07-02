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
    role: "Electrical Engineer",
    // One punchy line under your name on the homepage:
    tagline: "Electronics Team Lead designing the battery & high-voltage hardware for a 600V electric race car.",
    location: "Cincinnati, OH",
    email: "willmattis86@gmail.com",

    // A short paragraph for the About section. Edit freely.
    about: "Electrical engineering student at the University of Cincinnati (B.S. May 2026) " +
      "and Electronics Team Lead at Bearcats Electric Racing, where I lead the design of the " +
      "electronics behind a Formula-style electric race car. My work spans the full battery " +
      "management system for the 600V powertrain — from cell-level sensing boards to the " +
      "high-voltage pre/discharge safety hardware and the master controller that ties it all " +
      "together — plus the CAN-based data-acquisition and wireless telemetry the team uses to " +
      "debug the car. Before this I co-founded X-Inator, a battery-materials startup that " +
      "raised over $50k to develop nanostructured electrode materials. I like taking a system " +
      "from schematic capture and simulation through PCB layout, bring-up, and on-car validation.",

    // Links shown as buttons. Delete a line to hide that button.
    // Leave the value as "" to hide it too.
    links: {
      email: "willmattis86@gmail.com",
      linkedin: "https://www.linkedin.com/in/william-mattis-2417ab1a2/",
      github: "https://github.com/willmattis",
      resume: "assets/files/William-Mattis-Resume.pdf"
    },

    // Skill chips shown in the About section.
    skills: [
      "Altium Designer", "Schematic Capture", "PCB Layout", "LTspice",
      "MATLAB", "Embedded C / C++", "Python", "Teensy / Arduino / ESP32",
      "CAN Bus", "isoSPI", "Battery Management (BMS)", "High-Voltage Safety",
      "Data Acquisition", "SolidWorks / NX", "3D Printing",
      "Soldering & Reflow", "Hardware Bring-up"
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
    { name: "X-Inator",                 blurb: "My battery-materials startup — co-founded and raised $50k+ to build hardware for producing nanostructured electrode materials." },
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
      role: "As Electronics Team Lead, I spearheaded the schematic capture, simulation, " +
        "and PCB layout of this board — including the cell-tap filtering and the isolated " +
        "isoSPI communication front-end — as part of the battery-management system I lead " +
        "development of for our 600V powertrain.",
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
      role: "As Electronics Team Lead, I drove the design of this master board — " +
        "integrating the Teensy with the isoSPI front-end, CAN interface, and output " +
        "drivers — and coordinated a team of seven students across the broader BMS, " +
        "HV-monitoring, and data-acquisition effort it ties together.",
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
      role: "As Electronics Team Lead, I designed the high-voltage measurement chain, the " +
        "pre/discharge circuit, and the isolated relay-drive circuitry on this board. I also " +
        "calculated and simulated the thermal performance of the tractive-system pre/discharge " +
        "circuit in MATLAB to size its components for the 600V powertrain.",
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
      role: "I designed the schematic and layout of this CAN HAT — controller, transceiver, " +
        "and Pi-header integration — as part of the data-acquisition system I developed to " +
        "read and write CAN messages for troubleshooting the powertrain (the same DAQ effort " +
        "that also carries vehicle telemetry over sub-1GHz HaLow Wi-Fi).",
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
      title: "X-Inator — Glovebox Antechamber",
      subtitle: "Inert-atmosphere airlock to handle lithium for coin-cell production",
      org: "X-Inator (Personal Start-Up)",
      group: "X-Inator",
      date: "2023–2025",
      status: "Startup",
      tags: ["CAD", "Mechanical", "Sealing", "Battery Materials", "Startup"],
      thumb: "assets/img/xinator-antechamber-1.jpg",
      model: "assets/files/x-inator-antechamber.step",
      summary: "X-Inator is the battery-materials startup I co-founded to develop nanostructured " +
        "electrode materials. This antechamber was designed to add a sealed airlock to an existing " +
        "glovebox — letting us pass materials in and out without breaking the inert atmosphere we " +
        "needed to keep lithium from reacting while building test coin cells.",
      role: "As co-founder, I designed and built this antechamber — along with the rest of our " +
        "production hardware, including a glovebox humidity-control loop, anode prototype molds, and " +
        "a 3000+ psi chamber for material production. I also helped raise over $50,000 in " +
        "non-dilutive funding through the UC Venture Lab and other donors.",
      highlights: [
        "Co-founded the startup and raised $50k+ in non-dilutive funding (UC Venture Lab + donors)",
        "Designed a sealed antechamber to retrofit an inert-atmosphere airlock onto an existing glovebox",
        "Achieved a reliable seal on the antechamber — the goal of keeping an inert environment intact",
        "Built to enable lithium handling for lab-made coin-cell battery production"
      ],
      sections: [
        { heading: "Overview", body: "X-Inator was a personal start-up focused on producing " +
          "nanostructured materials for battery electrodes. Building and testing those materials as " +
          "coin cells meant handling lithium, which reacts in open air — so it has to be worked in an " +
          "inert atmosphere. This antechamber was designed to add a proper airlock to an existing " +
          "glovebox so materials could be moved in and out without losing that inert environment." },
        { heading: "Design & outcome", body: "I designed the antechamber to seal reliably, and it " +
          "did — it held the airlock seal we needed. The limiting factor turned out to be the existing " +
          "glovebox itself, which struggled to stay sealed; that ultimately led us to move to a new " +
          "glovebox for storing our materials. The antechamber work proved out the sealing approach " +
          "and clarified where the real leak path was." }
      ],
      specs: [
        { label: "Venture", value: "Co-founder, X-Inator" },
        { label: "Funding", value: "$50k+ (non-dilutive)" },
        { label: "Function", value: "Glovebox airlock / antechamber" },
        { label: "Atmosphere", value: "Inert (lithium handling)" },
        { label: "Application", value: "Coin-cell battery production" },
        { label: "Tool", value: "SolidWorks / NX" }
      ],
      gallery: [
        { src: "assets/img/xinator-antechamber-1.jpg", caption: "Antechamber assembly" },
        { src: "assets/img/xinator-antechamber-2.jpg", caption: "" },
        { src: "assets/img/xinator-antechamber-3.jpg", caption: "" },
        { src: "assets/img/xinator-antechamber-4.jpg", caption: "" },
        { src: "assets/img/xinator-antechamber-5.jpg", caption: "" }
      ],
      files: [
        { label: "3D model (STEP)", href: "assets/files/x-inator-antechamber.step", kind: "step" }
      ],
      links: []
    },

    {
      slug: "x-inator-aerogel",
      title: "X-Inator — Aerogel Manufacturing",
      subtitle: "Producing & characterizing the nanostructured electrode material",
      org: "X-Inator (Personal Start-Up)",
      group: "X-Inator",
      date: "2023–2025",
      status: "Startup",
      tags: ["Materials", "Nanostructures", "Aerogel", "SEM", "Startup"],
      thumb: "assets/img/xinator-aerogel-sem-1.jpg",
      summary: "The aerogel was the material X-Inator was built around — a nanostructured electrode " +
        "material we produced and characterized in-house. " +
        "// EDIT: add a sentence on what the aerogel is and how it was made.",
      role: "As co-founder, I developed and ran the production process for the material and " +
        "characterized the results under a scanning electron microscope (SEM). " +
        "// EDIT: describe exactly your part in the chemistry / process.",
      highlights: [
        "Produced a nanostructured aerogel material for use as a battery electrode",
        "Characterized the material's nanostructure on a scanning electron microscope (SEM)",
        "// EDIT — add a specific process detail or result (e.g. precursor, drying method, structure seen)"
      ],
      sections: [
        { heading: "Overview", body: "X-Inator's core product was a nanostructured material for " +
          "battery electrodes, made as an aerogel. Producing it in-house meant developing a repeatable " +
          "process and then verifying the resulting nanostructure. " +
          "// EDIT: describe the goal and the process at a high level." },
        { heading: "Characterization", body: "We imaged the material on a scanning electron microscope " +
          "to confirm its nanostructure. " +
          "// EDIT: describe what the SEM images showed and how it informed the process." }
      ],
      specs: [
        { label: "Material", value: "Nanostructured aerogel (battery electrode)" },
        { label: "Characterization", value: "Scanning electron microscope (SEM)" },
        { label: "Venture", value: "Co-founder, X-Inator" },
        { label: "Tool", value: "// EDIT — process equipment / software" }
      ],
      gallery: [
        { src: "assets/img/xinator-aerogel-sem-1.jpg", caption: "SEM imaging of the nanostructured material" },
        { src: "assets/img/xinator-aerogel-sem-2.jpg", caption: "SEM imaging" },
        { src: "assets/img/xinator-aerogel-sem-3.jpg", caption: "SEM imaging" },
        { src: "assets/img/xinator-aerogel-1.jpg", caption: "" },
        { src: "assets/img/xinator-aerogel-2.jpg", caption: "" },
        { src: "assets/img/xinator-aerogel-3.jpg", caption: "" },
        { src: "assets/img/xinator-aerogel-4.jpg", caption: "" },
        { src: "assets/img/xinator-aerogel-5.jpg", caption: "" },
        { src: "assets/img/xinator-aerogel-6.jpg", caption: "" },
        { src: "assets/img/xinator-aerogel-7.jpg", caption: "" },
        { src: "assets/img/xinator-aerogel-8.jpg", caption: "" },
        { src: "assets/img/xinator-aerogel-9.jpg", caption: "" },
        { src: "assets/img/xinator-aerogel-10.jpg", caption: "" },
        { src: "assets/img/xinator-aerogel-11.jpg", caption: "" },
        { src: "assets/img/xinator-aerogel-12.jpg", caption: "" },
        { src: "assets/img/xinator-aerogel-13.jpg", caption: "" },
        { src: "assets/img/xinator-aerogel-14.jpg", caption: "" }
      ],
      files: [],
      links: []
    },

    {
      slug: "x-inator-coin-cell",
      title: "X-Inator — Coin Cell Manufacturing",
      subtitle: "Assembling lab-made coin cells to test the electrode material",
      org: "X-Inator (Personal Start-Up)",
      group: "X-Inator",
      date: "2023–2025",
      status: "Startup",
      tags: ["Batteries", "Coin Cell", "Lithium", "Testing", "Startup"],
      thumb: "assets/img/xinator-coincell-1.jpg",
      summary: "To find out whether the aerogel material actually worked as an electrode, we built " +
        "lab-made coin-cell batteries with it and tested them — assembled inside an inert atmosphere " +
        "to keep the lithium from reacting.",
      role: "As co-founder, I assembled and tested the coin cells using our in-house material. " +
        "// EDIT: describe the cell build, what you measured, and the results.",
      highlights: [
        "Produced lab-made coin-cell batteries using our own nanostructured electrode material",
        "Assembled in an inert atmosphere to safely handle lithium",
        "// EDIT — add what you tested (capacity, cycling, etc.) and any result"
      ],
      sections: [
        { heading: "Overview", body: "Coin cells were how we validated the material end to end — " +
          "building a real battery with our electrode and measuring how it performed. " +
          "// EDIT: describe the cell construction and test goals." },
        { heading: "Process", body: "Because the cells use lithium, assembly happened inside an inert " +
          "environment. " +
          "// EDIT: describe your assembly steps and what the results told you." }
      ],
      specs: [
        { label: "Output", value: "Lab-made coin-cell batteries" },
        { label: "Environment", value: "Inert atmosphere (lithium handling)" },
        { label: "Venture", value: "Co-founder, X-Inator" },
        { label: "Tool", value: "// EDIT — test equipment" }
      ],
      gallery: [
        { src: "assets/img/xinator-coincell-1.jpg", caption: "" },
        { src: "assets/img/xinator-coincell-2.jpg", caption: "" },
        { src: "assets/img/xinator-coincell-3.jpg", caption: "" },
        { src: "assets/img/xinator-coincell-4.jpg", caption: "" },
        { src: "assets/img/xinator-coincell-5.jpg", caption: "" },
        { src: "assets/img/xinator-coincell-6.jpg", caption: "" },
        { src: "assets/img/xinator-coincell-7.jpg", caption: "" },
        { src: "assets/img/xinator-coincell-8.jpg", caption: "" },
        { src: "assets/img/xinator-coincell-9.jpg", caption: "" }
      ],
      files: [],
      links: []
    },

    /* ===================== SCHOOL PROJECTS ================================= */
    {
      slug: "dc-motor-assembly",
      title: "DC Motor Assembly",
      subtitle: "DC motor designed and modeled for Electromagnetics coursework",
      org: "University of Cincinnati — Electromagnetics",
      group: "School Projects",
      date: "2026",
      status: "Built",
      tags: ["CAD", "Electromagnetics", "DC Motor", "Electromechanical"],
      thumb: "assets/img/motor-1.jpg",
      model: "assets/files/dc-motor.step",
      summary: "A DC motor I designed and modeled for my Electromagnetics course — a hands-on way " +
        "to show the real-world application of the magnetic and electric field theory we covered in " +
        "class, built up as a full electromechanical CAD assembly.",
      role: "I designed and modeled the complete DC motor assembly in CAD, translating the " +
        "course's field theory into a working electromechanical design — rotor, stator, and housing.",
      highlights: [
        "Built for an Electromagnetics course to demonstrate magnetic and electric fields in practice",
        "Full 3D CAD assembly of a DC motor — rotor, stator, and housing",
        "Connects classroom field theory to a tangible, real-world device"
      ],
      sections: [
        { heading: "Overview", body: "This project was built for my Electromagnetics course at the " +
          "University of Cincinnati. The goal was to show the real-world application of what we " +
          "learned in class — how magnetic and electric fields combine to produce motion — by " +
          "designing and modeling an actual DC motor rather than just working the math on paper." },
        { heading: "Design", body: "I modeled the motor as a complete electromechanical assembly " +
          "in CAD, working through how the field interactions between the rotor and stator drive the " +
          "motor. It ties the course's electromagnetic theory directly to the geometry of a device " +
          "that uses it." }
      ],
      specs: [
        { label: "Type", value: "DC motor assembly" },
        { label: "Course", value: "Electromagnetics (UC)" },
        { label: "Goal", value: "Apply magnetic & electric field theory" },
        { label: "Tool", value: "SolidWorks / NX" }
      ],
      gallery: [
        { src: "assets/img/motor-1.jpg", caption: "// EDIT caption" },
        { src: "assets/img/motor-2.jpg", caption: "" }
      ],
      files: [
        { label: "3D model (STEP)", href: "assets/files/dc-motor.step", kind: "step" }
      ],
      links: []
    },

    {
      slug: "phototransistor-optocouplers",
      title: "Phototransistors & Optocouplers",
      subtitle: "Optoelectronics study with interactive photoconductivity simulations",
      org: "University of Cincinnati — Fundamentals of Optoelectronics",
      group: "School Projects",
      date: "Spring 2026",
      status: "Presentation",
      tags: ["Optoelectronics", "Phototransistors", "Optocouplers", "Python", "Simulation"],
      thumb: "assets/img/photo-optocoupler-1.png",
      summary: "A deep dive into phototransistors and optocouplers for my Fundamentals of " +
        "Optoelectronics course: I derived the governing photoconductivity equations and built two " +
        "interactive Python simulations. It connects directly to my Bearcats work — an optocoupler " +
        "photo-relay is what isolates the 600V and 12V sides on the HV sense board.",
      role: "I researched the topic, worked through the full derivation of the optocoupler/" +
        "phototransistor equations from the Petritz photoconductivity model, and wrote two interactive " +
        "Python simulations to make the behavior tangible. I presented the work to the class.",
      highlights: [
        "Derived the optocoupler current-transfer ratio (CTR) from the Petritz photoconductivity model — " +
          "CTR ∝ β·Γₒₜ·η·(1+B)·τ/τₜ",
        "Built an interactive optocoupler simulation with live sliders for LED forward current (I_F), " +
          "collector–emitter voltage (V_CE), and temperature",
        "Built a waveguide simulation showing how lateral illumination improves injection efficiency vs free space",
        "Compared Si, GaAs, and InP for optical-fiber operation (wavelength, band gap, attenuation)",
        "Tied it back to a real application: the optocoupler isolating 600V/12V on the EV4 HV sense board"
      ],
      sections: [
        { heading: "Overview", body: "Optocouplers use an LED and a phototransistor to pass a signal " +
          "across a galvanic isolation barrier — exactly what's needed to safely sense a high-voltage " +
          "system from low-voltage electronics. For this Fundamentals of Optoelectronics project I " +
          "studied how that pairing works, from the device physics up to a working circuit model." },
        { heading: "Deriving the equations", body: "Starting from the Petritz “theory of " +
          "photoconductivity in semiconductor films,” I worked through the change in carrier density, " +
          "steady-state conductivity, specific responsivity, and apparent quantum efficiency to arrive at " +
          "the current-transfer ratio — the optocoupler's equivalent of transistor β — and how it " +
          "depends on the LED current, photocarrier lifetime, and temperature." },
        { heading: "Optocoupler simulation", body: "I wrote a real-time Python simulation of the " +
          "optocoupler's photoconductivity. Sliders for LED forward current, collector–emitter voltage, " +
          "and temperature update plots of CTR vs current, relative CTR vs temperature, the base " +
          "junction's photodiode I–V, and the phototransistor's I_C vs V_CE, with a live operating-point readout." },
        { heading: "Waveguide simulation", body: "A second simulation compares feeding light into the " +
          "phototransistor through a waveguide (lateral illumination) against free-space injection, showing " +
          "how the waveguide improves coupling efficiency into the absorption region." }
      ],
      specs: [
        { label: "Course", value: "Fundamentals of Optoelectronics (UC)" },
        { label: "Topic", value: "Phototransistors & optocouplers" },
        { label: "Model", value: "Petritz photoconductivity" },
        { label: "Simulations", value: "Python (Matplotlib)" },
        { label: "Term", value: "Spring 2026" }
      ],
      gallery: [
        { src: "assets/img/photo-optocoupler-1.png", caption: "Interactive optocoupler photoconductivity simulation (Petritz model / ANO007)" },
        { src: "assets/img/photo-optocoupler-2.png", caption: "Optocoupler simulation at a different operating point" },
        { src: "assets/img/photo-waveguide-1.png", caption: "Waveguide vs free-space injection efficiency" },
        { src: "assets/img/photo-waveguide-2.png", caption: "Waveguide simulation" }
      ],
      files: [
        { label: "Presentation (PDF)", href: "assets/files/phototransistor-presentation.pdf", kind: "pdf" },
        { label: "Optocoupler simulation (Python)", href: "assets/files/optocoupler_sim.py", kind: "file" },
        { label: "Waveguide simulation (Python)", href: "assets/files/waveguide_sim.py", kind: "file" }
      ],
      links: []
    }

  ]
};
