# =========================================================
# HYDROSCOPE WATER INTERACTION ENGINE
# =========================================================

st.html(
    """
    <style>

    /* =====================================================
       GLOBAL WATER SURFACE
       ===================================================== */

    html, body {
        scroll-behavior: smooth;
    }

    body {
        overflow-x: hidden;
    }


    /* =====================================================
       WATER LIGHT FOLLOWING CURSOR
       ===================================================== */

    #hydro-cursor-light {
        position: fixed;

        width: 420px;
        height: 420px;

        border-radius: 50%;

        pointer-events: none;

        z-index: 999999;

        transform: translate(-50%, -50%);

        background:
            radial-gradient(
                circle,
                rgba(56, 189, 248, 0.075) 0%,
                rgba(14, 165, 233, 0.035) 30%,
                transparent 70%
            );

        filter: blur(2px);

        opacity: 0;

        transition: opacity 0.3s ease;
    }


    /* =====================================================
       RIPPLE
       ===================================================== */

    .hydro-ripple {

        position: fixed;

        pointer-events: none;

        z-index: 999998;

        width: 15px;
        height: 15px;

        border-radius: 50%;

        transform:
            translate(-50%, -50%)
            scale(0);

        border:
            1px solid rgba(125, 211, 252, 0.75);

        background:
            radial-gradient(
                circle,
                rgba(56, 189, 248, 0.16),
                rgba(56, 189, 248, 0.04) 45%,
                transparent 70%
            );

        box-shadow:
            0 0 25px rgba(56, 189, 248, 0.15);

        animation:
            hydroRipple 1.25s cubic-bezier(
                0.15,
                0.75,
                0.35,
                1
            ) forwards;
    }

    @keyframes hydroRipple {

        0% {
            width: 15px;
            height: 15px;
            opacity: 0.9;
            transform:
                translate(-50%, -50%)
                scale(0);
        }

        35% {
            opacity: 0.65;
        }

        100% {
            width: 420px;
            height: 420px;
            opacity: 0;
            transform:
                translate(-50%, -50%)
                scale(1);
        }
    }


    /* =====================================================
       SECONDARY RIPPLE
       ===================================================== */

    .hydro-ripple::after {

        content: "";

        position: absolute;

        inset: 25px;

        border-radius: 50%;

        border:
            1px solid rgba(186, 230, 253, 0.35);
    }


    /* =====================================================
       BUTTON WATER EFFECT
       ===================================================== */

    .stButton > button {

        position: relative;

        overflow: hidden;

        border-radius: 14px !important;

        border:
            1px solid rgba(
                125,
                211,
                252,
                0.18
            ) !important;

        background:
            linear-gradient(
                135deg,
                rgba(17, 51, 76, 0.72),
                rgba(5, 27, 46, 0.62)
            ) !important;

        color: #bcecff !important;

        backdrop-filter: blur(16px);

        transition:
            transform 0.22s ease,
            box-shadow 0.22s ease,
            border-color 0.22s ease !important;
    }


    /* glowing water line */

    .stButton > button::before {

        content: "";

        position: absolute;

        top: 0;
        left: -120%;

        width: 90%;
        height: 100%;

        background:
            linear-gradient(
                90deg,
                transparent,
                rgba(125, 211, 252, 0.18),
                transparent
            );

        transform: skewX(-20deg);

        transition: left 0.6s ease;

        pointer-events: none;
    }


    .stButton > button:hover::before {
        left: 140%;
    }


    .stButton > button:hover {

        transform:
            translateY(-3px);

        border-color:
            rgba(56, 189, 248, 0.48) !important;

        box-shadow:
            0 10px 30px rgba(
                14,
                165,
                233,
                0.16
            ),
            inset 0 1px 0
            rgba(255,255,255,0.08);

        color: #e8faff !important;
    }


    .stButton > button:active {

        transform:
            translateY(1px)
            scale(0.97);

        box-shadow:
            0 0 30px
            rgba(56, 189, 248, 0.3);
    }


    /* =====================================================
       GLASS SURFACES
       ===================================================== */

    .glass-card {

        background:
            linear-gradient(
                135deg,
                rgba(17, 45, 70, 0.68),
                rgba(3, 23, 40, 0.48)
            );

        border:
            1px solid rgba(
                125,
                211,
                252,
                0.15
            );

        backdrop-filter:
            blur(22px)
            saturate(135%);

        -webkit-backdrop-filter:
            blur(22px)
            saturate(135%);

        box-shadow:
            0 20px 50px
            rgba(0, 0, 0, 0.22),

            inset 0 1px 0
            rgba(255,255,255,0.07);

        transition:
            transform 0.35s ease,
            border-color 0.35s ease,
            box-shadow 0.35s ease;
    }


    .glass-card:hover {

        transform:
            translateY(-5px);

        border-color:
            rgba(56,189,248,0.30);

        box-shadow:
            0 25px 60px
            rgba(0,0,0,0.28),

            0 0 35px
            rgba(56,189,248,0.07),

            inset 0 1px 0
            rgba(255,255,255,0.09);
    }


    /* =====================================================
       LIQUID SHIMMER
       ===================================================== */

    .liquid-shimmer {

        position: relative;

        overflow: hidden;
    }

    .liquid-shimmer::after {

        content: "";

        position: absolute;

        width: 180%;
        height: 100%;

        top: 0;
        left: -180%;

        background:
            linear-gradient(
                110deg,
                transparent 35%,
                rgba(255,255,255,0.035) 48%,
                rgba(125,211,252,0.08) 50%,
                transparent 62%
            );

        animation:
            liquidSweep 7s
            ease-in-out
            infinite;

        pointer-events: none;
    }


    @keyframes liquidSweep {

        0% {
            left: -180%;
        }

        45% {
            left: 160%;
        }

        100% {
            left: 160%;
        }
    }


    /* =====================================================
       WATER WAVE AT BOTTOM
       ===================================================== */

    .hydro-wave {

        position: fixed;

        bottom: -55px;

        left: -5%;

        width: 110%;

        height: 100px;

        border-radius: 50%;

        pointer-events: none;

        z-index: 0;

        background:
            radial-gradient(
                ellipse,
                rgba(14,165,233,0.08),
                transparent 68%
            );

        animation:
            hydroWave 8s
            ease-in-out
            infinite;
    }


    @keyframes hydroWave {

        0%,100% {
            transform:
                translateX(-2%)
                rotate(-1deg);
        }

        50% {
            transform:
                translateX(2%)
                rotate(1deg);
        }
    }

    </style>


    <!-- CURSOR WATER LIGHT -->

    <div id="hydro-cursor-light"></div>

    <!-- AMBIENT WATER -->

    <div class="hydro-wave"></div>


    <script>

    /* =====================================================
       CURSOR LIGHT
       ===================================================== */

    const light =
        document.getElementById(
            "hydro-cursor-light"
        );

    document.addEventListener(
        "pointermove",
        function(event) {

            light.style.left =
                event.clientX + "px";

            light.style.top =
                event.clientY + "px";

            light.style.opacity = "1";
        }
    );


    /* =====================================================
       WATER RIPPLE ON ANY CLICK / TOUCH
       ===================================================== */

    document.addEventListener(
        "pointerdown",
        function(event) {

            const ripple =
                document.createElement("div");

            ripple.className =
                "hydro-ripple";

            ripple.style.left =
                event.clientX + "px";

            ripple.style.top =
                event.clientY + "px";

            document.body.appendChild(ripple);


            setTimeout(
                function() {
                    ripple.remove();
                },
                1400
            );

        },
        { passive: true }
    );


    /* =====================================================
       BUTTON SPLASH
       ===================================================== */

    document.addEventListener(
        "pointerdown",
        function(event) {

            const button =
                event.target.closest(
                    "button"
                );

            if (!button) {
                return;
            }

            const splash =
                document.createElement("span");

            splash.style.position =
                "absolute";

            splash.style.left =
                event.clientX -
                button.getBoundingClientRect().left +
                "px";

            splash.style.top =
                event.clientY -
                button.getBoundingClientRect().top +
                "px";

            splash.style.width = "12px";
            splash.style.height = "12px";

            splash.style.borderRadius =
                "50%";

            splash.style.background =
                "rgba(125,211,252,0.35)";

            splash.style.transform =
                "translate(-50%,-50%) scale(0)";

            splash.style.pointerEvents =
                "none";

            splash.style.transition =
                "transform 0.65s ease, opacity 0.65s ease";

            button.appendChild(splash);


            requestAnimationFrame(
                function() {

                    splash.style.transform =
                        "translate(-50%,-50%) scale(18)";

                    splash.style.opacity =
                        "0";

                }
            );


            setTimeout(
                function() {
                    splash.remove();
                },
                700
            );

        },
        { passive: true }
    );

    </script>
    """,
    unsafe_allow_javascript=True
)
