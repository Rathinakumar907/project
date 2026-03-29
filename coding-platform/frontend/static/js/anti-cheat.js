// anti-cheat.js

window.initAntiCheat = function (sessionToken) {
    console.log("Anti-Cheat System Initialized for session:", sessionToken);

    let violationCount = 0;
    let pasteTimestamps = [];

    // Behavior telemetry state
    let charCount = 0;
    let sessionPasteCount = 0;
    let sessionTotalPasteSize = 0;
    let lastActive = Date.now();

    // Prevent Context Menu (Right Click)
    document.addEventListener("contextmenu", (e) => {
        e.preventDefault();
        logViolation("Context menu opened (right-click)", true);
    });

    // Prevent Copy/Paste on the document body
    document.addEventListener("copy", (e) => {
        e.preventDefault();
        logViolation("Copy action detected", false);
    });

    document.addEventListener("paste", (e) => {
        // Monaco handles paste internally sometimes, but this catches native document-level paste attempts
        const clipboardData = e.clipboardData || window.clipboardData;
        const pastedData = clipboardData.getData('Text');
        
        // Track paste frequency
        const now = Date.now();
        lastActive = now;
        pasteTimestamps = pasteTimestamps.filter(ts => now - ts < 60000); // Only keep last 1 minute
        pasteTimestamps.push(now);

        sessionPasteCount++;
        sessionTotalPasteSize += pastedData.length;

        if (pasteTimestamps.length > 5) {
            e.preventDefault(); // Prevent paste if too frequent
            logViolation("Paste abuse detected (too many pastes in 1 min)", true);
        } else if (pastedData.split('\n').length > 10) {
            e.preventDefault(); // Prevent paste if too large
            logViolation(`Large block paste detected (${pastedData.split('\n').length} lines)`, true);
        }
    });

    // Detect Tab Switch / Loss of Focus
    window.addEventListener("blur", () => {
        logViolation("Tab switch or loss of focus detected", true);
    });

    document.addEventListener("visibilitychange", () => {
        if (document.hidden) {
            logViolation("Tab switching is not allowed", true);
        }
    });

    // Detect Fullscreen Exit
    document.addEventListener("fullscreenchange", () => {
        if (!document.fullscreenElement) {
            logViolation("Do not exit fullscreen during exam", true);
        }
    });

    async function logViolation(reason, showWarning) {
        if (violationCount >= 3) return;

        // --- BACKEND REPORTING ---
        if (sessionToken) {
            try {
                const res = await authFetch(`${API_BASE}/student/exam/violation`, {
                    method: "POST",
                    headers: { "X-Exam-Session": sessionToken },
                    body: JSON.stringify({
                        event_type: reason,
                        metadata_json: JSON.stringify({ url: window.location.href, ts: new Date().toISOString() })
                    })
                });
                if (res && res.ok) {
                    const data = await res.json();
                    violationCount = data.violation_count;
                }
            } catch (err) {
                console.error("Failed to log violation to backend:", err);
            }
        }

        console.warn(`[ANTI-CHEAT] Violation #${violationCount}: ${reason}`);

        if (showWarning) {
            const modal = document.getElementById("cheat-modal");
            const countSpan = document.getElementById("warn-count");
            const reasonSpan = document.getElementById("warn-reason");

            if (modal && countSpan && reasonSpan) {
                countSpan.innerText = violationCount;
                reasonSpan.innerText = reason;

                modal.classList.add("active");
                modal.style.display = "flex";
            }
        }

        if (violationCount >= 3) {
            // Auto-submit code as cheat detected immediately on 3rd violation
            if (typeof submitCode === "function") {
                const modal = document.getElementById("cheat-modal");
                if (modal) {
                    modal.innerHTML = `
                        <div style="background: var(--bg-color-secondary); padding: 24px; border-radius: 8px; border: 1px solid var(--danger); max-width: 400px; text-align: center;">
                            <h3 style="color: var(--danger); margin-top: 0;">Exam Terminated</h3>
                            <p style="margin: 16px 0; color: var(--text-primary);">You have exceeded the maximum number of warnings.</p>
                            <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 24px;">Automatically submitting your code...</p>
                            <div style="display: flex; gap: 8px; justify-content: center;">
                                <button class="btn btn-secondary" style="background: var(--glass-border); color: white;" onclick="window.location.href='/student/dashboard'">Return to Dashboard</button>
                            </div>
                        </div>
                     `;
                    modal.style.display = "flex";
                }
                submitCode(true); // Call submitCode with isCheat=true
            }
        }
    }

    // Track typing speed, activity, and block shortcuts
    document.addEventListener("keydown", (e) => {
        const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
        const mainModifier = isMac ? e.metaKey : e.ctrlKey;
        
        let shouldBlock = false;
        let blockedKey = "";

        if (e.key === "F11") {
            shouldBlock = true;
            blockedKey = "F11";
        } else if (e.key === "Escape") {
            // Natural fullscreen exit handled by fullscreenchange, but log attempt
        } else if (e.altKey && e.key === "Tab") {
            shouldBlock = true;
            blockedKey = "Alt+Tab";
        } else if (mainModifier && (e.key.toLowerCase() === "c" || e.key.toLowerCase() === "v")) {
            shouldBlock = true;
            blockedKey = isMac ? "Cmd+C/V" : "Ctrl+C/V";
        } else if (mainModifier && (e.key.toLowerCase() === "w" || e.key.toLowerCase() === "t")) {
            shouldBlock = true;
            blockedKey = isMac ? "Cmd+W/T" : "Ctrl+W/T";
        }

        if (shouldBlock) {
            e.preventDefault();
            e.stopPropagation();
            logViolation(`Keyboard shortcut blocked (${blockedKey})`, true);
        }

        charCount++;
        lastActive = Date.now();
    });

    document.addEventListener("mousemove", () => {
        lastActive = Date.now();
    });

    // Periodically sync behavior telemetry (every 30s)
    setInterval(async () => {
        if (!sessionToken) return;

        const idleTime = Math.floor((Date.now() - lastActive) / 1000);
        const typingSpeed = charCount; // chars per interval

        try {
            await authFetch(`${API_BASE}/student/exam/behavior`, {
                method: "POST",
                headers: { "X-Exam-Session": sessionToken },
                body: JSON.stringify({
                    typing_speed: typingSpeed,
                    paste_count: sessionPasteCount,
                    paste_size: sessionTotalPasteSize,
                    idle_time: idleTime
                })
            });
            // Reset interval counters
            charCount = 0;
            sessionPasteCount = 0;
            sessionTotalPasteSize = 0;
        } catch (err) {
            console.error("Telemetry sync failed:", err);
        }
    }, 30000);

    // Run environment checks immediately
    (async () => {
        const suspicious = [];
        try {
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
            if (gl) {
                const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                if (debugInfo) {
                    const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
                    const vendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
                    if (/llvm|swiftshader|mesa|virtualbox|vmware|parallel|citrix|hyper-v/i.test(renderer + vendor)) {
                        suspicious.push(`Virtual GPU: ${renderer}`);
                    }
                }
            }
        } catch (e) { }

        if (navigator.hardwareConcurrency && navigator.hardwareConcurrency < 2) {
            suspicious.push(`Low CPU threads: ${navigator.hardwareConcurrency}`);
        }

        if (window.screen.availWidth > window.screen.width) {
            suspicious.push("Multi-monitor detected");
        }

        if (suspicious.length > 0) {
            console.warn("[ANTI-CHEAT] Suspicious environment detected:", suspicious);
            await logViolation(`Environment Alert: ${suspicious.join(', ')}`, false);
        }
    })();
};

function hideCheatWarning() {
    const modal = document.getElementById("cheat-modal");
    if (modal) {
        modal.classList.remove("active");
        modal.style.display = "none";
    }
}
