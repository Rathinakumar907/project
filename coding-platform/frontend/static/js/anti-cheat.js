// anti-cheat.js

window.initAntiCheat = function () {
    console.log("Anti-Cheat System Initialized.");

    let violationCount = 0;

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

        // Simple heuristic: instant large paste is suspicious
        if (pastedData.split('\n').length > 10) {
            e.preventDefault();
            logViolation(`Large block paste detected (${pastedData.split('\n').length} lines)`, true);
        }
    });

    // Detect Tab Switch / Loss of Focus
    window.addEventListener("blur", () => {
        logViolation("Tab switch or loss of focus detected", true);
    });

    function logViolation(reason, showWarning) {
        if (violationCount >= 3) return; // Prevent spamming after test conclusion

        violationCount++;
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

    // Example auto-submission interval or other listeners can go here
};

function hideCheatWarning() {
    const modal = document.getElementById("cheat-modal");
    if (modal) {
        modal.classList.remove("active");
        modal.style.display = "none";
    }
}
