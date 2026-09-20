async function loadPatientCount() {
    try {
        const data = await apiFetch("/");
        document.getElementById("patientsCount").textContent =
            data.patients_indexed ?? "—";
    } catch (error) {
        document.getElementById("patientsCount").textContent = "—";
    }
}
/* =========================================================
   HEALTHCARE BLOCKCHAIN FRONTEND
========================================================= */

const API = "http://127.0.0.1:8000";

let currentUser = null;
let selectedPatient = null;
let selectedEncounter = null;


/* =========================================================
   BASIC HELPERS
========================================================= */

async function apiFetch(endpoint, options = {}) {

    const response = await fetch(API + endpoint, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {})
        }
    });

    let data;

    try {
        data = await response.json();
    } catch {
        data = {};
    }

    if (!response.ok) {

        const message =
            data.detail ||
            data.message ||
            "API request failed";

        throw new Error(message);
    }

    return data;
}


function showToast(message) {

    const toast = document.getElementById("toast");

    toast.textContent = message;

    toast.classList.remove("hidden");

    setTimeout(() => {
        toast.classList.add("hidden");
    }, 3500);
}


function escapeHtml(value) {

    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


/* =========================================================
   LOGIN
========================================================= */

document
    .getElementById("loginBtn")
    .addEventListener("click", login);


async function login() {

    const username =
        document.getElementById("username").value.trim();

    const password =
        document.getElementById("password").value.trim();

    const message =
        document.getElementById("loginMessage");


    if (!username || !password) {

        message.textContent =
            "Enter username and password.";

        message.className =
            "message";

        return;
    }


    try {

        const data = await apiFetch(
            "/api/auth/login",
            {
                method: "POST",

                body: JSON.stringify({
                    username,
                    password
                })
            }
        );


        currentUser = data;

        sessionStorage.setItem(
            "healthcareUser",
            JSON.stringify(data)
        );


        openDashboard();


    } catch (error) {

        message.textContent =
            error.message;

        message.className =
            "message";

    }
}


/* =========================================================
   DEMO ACCOUNT BUTTONS
========================================================= */

document
    .querySelectorAll(".demo-btn")
    .forEach(button => {

        button.addEventListener("click", () => {

            document.getElementById("username").value =
                button.dataset.user;

            document.getElementById("password").value =
                button.dataset.pass;

            login();

        });

    });


/* =========================================================
   OPEN DASHBOARD
========================================================= */
/* =========================================================
   ROLE-BASED DASHBOARD VISIBILITY
========================================================= */

function applyRoleBasedUI() {

    if (!currentUser) return;

    const role =
        String(currentUser.role || "").toUpperCase();

    const orgName =
        String(currentUser.org_name || "").toUpperCase();


    const patientSection =
        document.getElementById("patientSection");

    const claimsPanel =
        document.getElementById("claimsPanel");

    const tamperPanel =
        document.querySelector(".tamper-panel");

    const blockchainPanel =
        document.getElementById("blockchainPanel");

    const auditPanel =
        document.getElementById("auditPanel");

    const benchmarkPanel =
        document.getElementById("benchmarkPanel");


    /* Hide role-specific sections first */

    [
        patientSection,
        claimsPanel,
        tamperPanel,
        blockchainPanel,
        auditPanel,
        benchmarkPanel
    ].forEach(section => {

        if (section) {
            section.classList.add("hidden");
        }

    });


    /* =====================================================
       HOSPITAL
       ===================================================== */

    if (role === "HOSPITAL") {

        if (patientSection) {
            patientSection.classList.remove("hidden");
        }

        /*
         * Hospital A gets the clinical tamper demonstration.
         * Hospital B focuses on cross-hospital retrieval
         * and integrity verification.
         */

        if (
            tamperPanel &&
            orgName.includes("LAHEY")
        ) {
            tamperPanel.classList.remove("hidden");
        }

        return;
    }


    /* =====================================================
       INSURANCE
       ===================================================== */

    if (role === "INSURANCE") {

        if (claimsPanel) {
            claimsPanel.classList.remove("hidden");
        }

        return;
    }


    /* =====================================================
       ADMIN
       ===================================================== */

    if (role === "ADMIN") {

        if (claimsPanel) {
            claimsPanel.classList.remove("hidden");
        }

        if (tamperPanel) {
            tamperPanel.classList.remove("hidden");
        }

        if (blockchainPanel) {
            blockchainPanel.classList.remove("hidden");
        }

        if (auditPanel) {
            auditPanel.classList.remove("hidden");
        }

        if (benchmarkPanel) {
            benchmarkPanel.classList.remove("hidden");
        }

        return;
    }

}


function openDashboard() {

    document
        .getElementById("loginScreen")
        .classList.add("hidden");

    document
        .getElementById("appScreen")
        .classList.remove("hidden");


    document.getElementById("orgName").textContent =
        currentUser.org_name || "Organization";


    document.getElementById("orgRole").textContent =
    currentUser.role || "ROLE";


    applyRoleBasedUI();

    loadDashboard();

}


/* =========================================================
   LOGOUT
========================================================= */

document
    .getElementById("logoutBtn")
    .addEventListener("click", () => {

        currentUser = null;

        selectedPatient = null;

        selectedEncounter = null;

        sessionStorage.removeItem("healthcareUser");

        location.reload();

    });


/* =========================================================
   DASHBOARD LOAD
========================================================= */

async function loadDashboard() {

    await Promise.allSettled([
        loadBlockchainSummary(),
        loadPatientCount(),
        loadBlocks(),
        loadAudit(),
    ]);

    checkBlockchain();
}


/* =========================================================
   BLOCKCHAIN SUMMARY
========================================================= */

async function loadBlockchainSummary() {

    try {

        const data =
            await apiFetch("/api/blockchain/summary");


        document.getElementById("blocksCount").textContent =
            data.total_blocks ?? "—";


        document.getElementById("transactionsCount").textContent =
            data.total_transactions ?? "—";


        document.getElementById("blockchainSummary").innerHTML = `

            <div class="chain-stat">
                <span>Total Blocks</span>
                <strong>${escapeHtml(data.total_blocks)}</strong>
            </div>

            <div class="chain-stat">
                <span>Transactions</span>
                <strong>${escapeHtml(data.total_transactions)}</strong>
            </div>

            <div class="chain-stat">
                <span>Difficulty</span>
                <strong>${escapeHtml(data.difficulty_target || "00")}</strong>
            </div>

            <div class="chain-stat">
                <span>Latest Block</span>
                <strong>#${escapeHtml(data.latest_block_index)}</strong>
            </div>

            <div class="chain-stat">
                <span>Ledger</span>
                <strong>SHA-256 Hash Linked</strong>
            </div>

        `;


    } catch (error) {

        document.getElementById(
            "blockchainSummary"
        ).textContent =
            "Unable to load blockchain.";

    }
}


/* =========================================================
   BLOCKCHAIN VALIDATION
========================================================= */

document
    .getElementById("validateChainBtn")
    .addEventListener("click", checkBlockchain);


async function checkBlockchain() {

    try {

        const data =
            await apiFetch("/api/blockchain/validate");


        const status =
            document.getElementById("ledgerStatus");

        const systemStatus =
            document.getElementById("systemStatus");

        const dot =
            document.getElementById("systemStatusDot");


        if (data.is_valid) {

            status.textContent = "VALID";

            status.className =
                "stat-value status-valid";

            systemStatus.textContent =
                "Blockchain Valid";

            dot.style.background =
                "#16a34a";

            showToast(
                `Blockchain validated: ${data.total_blocks_verified} blocks verified.`
            );

        } else {

            status.textContent = "CORRUPTED";

            status.className =
                "stat-value invalid-badge";

            systemStatus.textContent =
                "Blockchain Integrity Alert";

            dot.style.background =
                "#dc2626";

            showToast(
                "Blockchain validation detected corruption."
            );
        }


    } catch (error) {

        showToast(
            "Blockchain validation failed."
        );

    }
}


/* =========================================================
   PATIENT SEARCH
========================================================= */

document
    .getElementById("searchPatientBtn")
    .addEventListener("click", searchPatients);


document
    .getElementById("patientSearch")
    .addEventListener("keydown", event => {

        if (event.key === "Enter") {
            searchPatients();
        }

    });


async function searchPatients() {

    const query =
        document
            .getElementById("patientSearch")
            .value
            .trim();


    if (!query) {

        showToast(
            "Enter a patient ID or name."
        );

        return;
    }


    const container =
        document.getElementById("searchResults");

    container.innerHTML =
        `<div class="loading">Searching...</div>`;


    try {

        const patients =
            await apiFetch(
                `/api/patients/search?q=${encodeURIComponent(query)}&limit=20`
            );


        if (!patients.length) {

            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">❌</div>
                    <p>No patients found.</p>
                </div>
            `;

            return;
        }


        container.innerHTML =
            patients.map(patient => `

                <div
                    class="patient-result"
                    data-id="${escapeHtml(patient.id)}">

                    <strong>
                        ${escapeHtml(patient.first_name)}
                        ${escapeHtml(patient.last_name)}
                    </strong>

                    <span>
                        ID: ${escapeHtml(patient.id)}
                    </span>

                    <span>
                        • ${escapeHtml(patient.gender)}
                        • ${escapeHtml(patient.city)}
                    </span>

                </div>

            `).join("");


        container
            .querySelectorAll(".patient-result")
            .forEach(element => {

                element.addEventListener(
                    "click",
                    () => selectPatient(element.dataset.id)
                );

            });


    } catch (error) {

        container.innerHTML = `
            <div class="empty-state">
                <p>
                    Search failed: ${escapeHtml(error.message)}
                </p>
            </div>
        `;

    }
}


/* =========================================================
   SELECT PATIENT
========================================================= */

async function selectPatient(patientId) {

    try {

        selectedPatient =
            await apiFetch(
                `/api/patients/${encodeURIComponent(patientId)}`
            );


        document
            .getElementById("patientSection")
            .classList.remove("hidden");


        document.getElementById(
            "selectedPatientName"
        ).textContent =
            `${selectedPatient.first_name} ${selectedPatient.last_name}`;


        document.getElementById(
            "selectedPatientMeta"
        ).textContent =
            `Patient ID: ${selectedPatient.id} • ${selectedPatient.gender} • ${selectedPatient.city}, ${selectedPatient.state}`;


        document
            .getElementById("ehrContainer")
            .classList.add("hidden");


        document
            .getElementById("integritySection")
            .classList.add("hidden");


        showToast(
            "Patient selected."
        );


    } catch (error) {

        showToast(
            error.message
        );

    }
}


/* =========================================================
   LOAD EHR
========================================================= */

document
    .getElementById("viewEhrBtn")
    .addEventListener("click", loadEHR);


async function loadEHR() {
    if (!selectedPatient) {
        showToast("Select a patient first.");
        return;
    }

    const container = document.getElementById("ehrContainer");
    container.classList.remove("hidden");

    document.getElementById("encounterList").innerHTML =
        '<div class="loading">Loading complete EHR...</div>';

    try {
        const data = await apiFetch(
            `/api/patients/${encodeURIComponent(selectedPatient.id)}/ehr?requesting_org=${encodeURIComponent(currentUser?.org_id || "HOSPITAL_USER")}`
        );

        const encounters = data.encounters || [];

        document.getElementById("encounterCount").textContent =
            encounters.length;

        if (!encounters.length) {
            document.getElementById("encounterList").innerHTML =
                '<div class="empty-state">No medical encounters found.</div>';
            return;
        }

        const patient = data.patient || selectedPatient;

        const renderItems = (items, fields) => {
            if (!items || !items.length) {
                return '<div class="empty-state">None recorded</div>';
            }

            return `
                <div class="ehr-items">
                    ${items.map(item => `
                        <div class="ehr-item">
                            ${fields.map(([label, key]) => `
                                <div>
                                    <span class="ehr-label">${label}</span>
                                    <strong>${escapeHtml(item[key] ?? "—")}</strong>
                                </div>
                            `).join("")}
                        </div>
                    `).join("")}
                </div>
            `;
        };

        document.getElementById("encounterList").innerHTML = `
            <div class="ehr-full-card">

                <div class="ehr-section-title">
                    <span class="section-label">PATIENT OVERVIEW</span>
                    <h3>${escapeHtml(patient.first_name || "")} ${escapeHtml(patient.last_name || "")}</h3>
                    <p>
                        Patient ID: ${escapeHtml(patient.id || "—")}
                        &nbsp; • &nbsp;
                        DOB: ${escapeHtml(patient.birthdate || "—")}
                        &nbsp; • &nbsp;
                        Gender: ${escapeHtml(patient.gender || "—")}
                    </p>
                    <p>
                        Location:
                        ${escapeHtml(patient.city || "—")},
                        ${escapeHtml(patient.state || "—")}
                        ${escapeHtml(patient.zip || "")}
                    </p>
                </div>

                <div class="ehr-section">
                    <div class="ehr-section-heading">
                        <h3>🏥 Medical Encounters</h3>
                        <span class="tag">${encounters.length}</span>
                    </div>

                    ${encounters.map((encounter, index) => `
                        <div
                            class="encounter-card"
                            data-encounter-id="${escapeHtml(encounter.encounter_id)}"
                        >
                            <div class="encounter-top">
                                <div class="encounter-title">
                                    ${escapeHtml(
                                        encounter.description ||
                                        encounter.encounter_class ||
                                        "Medical Encounter"
                                    )}
                                </div>

                                <div class="encounter-date">
                                    ${escapeHtml(encounter.start_time || "")}
                                </div>
                            </div>

                            <div class="encounter-description">
                                Hospital:
                                ${escapeHtml(encounter.organization_id || "Unknown")}
                            </div>

                            <div class="encounter-meta">
                                <span class="tag">
                                    Encounter: ${escapeHtml(encounter.encounter_id)}
                                </span>
                                <span class="tag">
                                    Block: ${escapeHtml(encounter.block_index)}
                                </span>
                                <span class="tag">
                                    Merkle Leaf: ${escapeHtml(encounter.merkle_leaf_index)}
                                </span>
                            </div>

                            <div class="ehr-subsection">
                                <h4>🩺 Conditions</h4>
                                ${renderItems(
                                    encounter.conditions,
                                    [
                                        ["Code", "code"],
                                        ["Description", "description"]
                                    ]
                                )}
                            </div>

                            <div class="ehr-subsection">
                                <h4>💊 Medications</h4>
                                ${renderItems(
                                    encounter.medications,
                                    [
                                        ["Code", "code"],
                                        ["Description", "description"],
                                        ["Dispenses", "dispenses"],
                                        ["Total Cost", "total_cost"]
                                    ]
                                )}
                            </div>

                            <div class="ehr-subsection">
                                <h4>🧪 Procedures</h4>
                                ${renderItems(
                                    encounter.procedures,
                                    [
                                        ["Code", "code"],
                                        ["Description", "description"]
                                    ]
                                )}
                            </div>

                            <div class="ehr-subsection">
                                <h4>💉 Immunizations</h4>
                                ${renderItems(
                                    encounter.immunizations,
                                    [
                                        ["Code", "code"],
                                        ["Description", "description"]
                                    ]
                                )}
                            </div>

                            <div class="ehr-subsection">
                                <h4>📊 Observations</h4>
                                ${renderItems(
                                    encounter.observations,
                                    [
                                        ["Category", "category"],
                                        ["Code", "code"],
                                        ["Description", "description"],
                                        ["Value", "value"],
                                        ["Units", "units"]
                                    ]
                                )}
                            </div>

                            <div class="ehr-subsection">
                                <h4>💳 Claims / Billing</h4>
                                ${renderItems(
                                    encounter.claims,
                                    [
                                        ["Claim ID", "id"],
                                        ["Status", "status"],
                                        ["Total Cost", "total_claim_cost"],
                                        ["Payer Coverage", "payer_coverage"],
                                        ["Diagnosis Code", "diagnosis_code"],
                                        ["Procedure Code", "procedure_code"]
                                    ]
                                )}
                            </div>

                            <div class="ehr-integrity">
                                <h4>🔐 Cryptographic Integrity</h4>

                                <div class="verification-grid">
                                    <div class="verification-item">
                                        <span>SHA-256 Record Hash</span>
                                        <strong>Stored on blockchain</strong>
                                    </div>

                                    <div class="verification-item">
                                        <span>Blockchain Block</span>
                                        <strong>#${escapeHtml(encounter.block_index)}</strong>
                                    </div>

                                    <div class="verification-item">
                                        <span>Merkle Leaf</span>
                                        <strong>${escapeHtml(encounter.merkle_leaf_index)}</strong>
                                    </div>
                                </div>

                                <p class="hash">
                                    Record Hash:
                                    ${escapeHtml(encounter.record_hash || "—")}
                                </p>
                            </div>

                            <button
                                class="outline-btn ehr-select-btn"
                                data-encounter-id="${escapeHtml(encounter.encounter_id)}"
                            >
                                Select This Encounter for Verification
                            </button>

                        </div>
                    `).join("")}
                </div>

                <div class="ehr-summary">
                    <h3>📋 EHR Summary</h3>

                    <div class="ehr-summary-grid">
                        <div>
                            <span>Encounters</span>
                            <strong>${encounters.length}</strong>
                        </div>

                        <div>
                            <span>Conditions</span>
                            <strong>${encounters.reduce((n, e) => n + (e.conditions?.length || 0), 0)}</strong>
                        </div>

                        <div>
                            <span>Medications</span>
                            <strong>${encounters.reduce((n, e) => n + (e.medications?.length || 0), 0)}</strong>
                        </div>

                        <div>
                            <span>Procedures</span>
                            <strong>${encounters.reduce((n, e) => n + (e.procedures?.length || 0), 0)}</strong>
                        </div>

                        <div>
                            <span>Observations</span>
                            <strong>${encounters.reduce((n, e) => n + (e.observations?.length || 0), 0)}</strong>
                        </div>

                        <div>
                            <span>Claims</span>
                            <strong>${encounters.reduce((n, e) => n + (e.claims?.length || 0), 0)}</strong>
                        </div>
                    </div>
                </div>

            </div>
        `;

        document
            .querySelectorAll(".ehr-select-btn")
            .forEach(button => {
                button.addEventListener("click", () => {
                    const encounterId = button.dataset.encounterId;
                    const card = button.closest(".encounter-card");
                    selectEncounter(encounterId, card);
                });
            });

        showToast("Complete EHR loaded successfully.");

    } catch (error) {
        document.getElementById("encounterList").innerHTML = `
            <div class="empty-state">
                Failed to load EHR:
                ${escapeHtml(error.message)}
            </div>
        `;

        showToast(error.message);
    }
}/* =========================================================
   SELECT ENCOUNTER
========================================================= */

function selectEncounter(encounterId, element) {

    selectedEncounter = encounterId;


    document
        .querySelectorAll(".encounter-card")
        .forEach(card => {
            card.classList.remove("selected");
        });


    element.classList.add("selected");


    document.getElementById(
        "tamperEncounterId"
    ).value =
        encounterId;


    document
        .getElementById("integritySection")
        .classList.remove("hidden");


    document.getElementById(
        "verificationResult"
    ).innerHTML = `

        <div class="verification-placeholder">

            🔐

            <p>
                Encounter ${escapeHtml(encounterId)}
                selected.
                Click <strong>Verify Record</strong>.
            </p>

        </div>

    `;


    showToast(
        `Encounter ${encounterId} selected.`
    );
}


/* =========================================================
   VERIFY ENCOUNTER
========================================================= */

document
    .getElementById("verifyBtn")
    .addEventListener("click", verifyEncounter);


async function verifyEncounter() {

    if (!selectedEncounter) {

        selectedEncounter =
            document
                .getElementById("tamperEncounterId")
                .value
                .trim();
    }


    if (!selectedEncounter) {

        showToast(
            "Select an encounter first."
        );

        return;
    }


    const result =
        document.getElementById(
            "verificationResult"
        );


    result.innerHTML =
        `<div class="loading">
            Verifying SHA-256 hash and Merkle proof...
        </div>`;


    try {

        const data =
            await apiFetch(
                `/api/encounters/${encodeURIComponent(selectedEncounter)}/verify?requesting_org=${encodeURIComponent(currentUser?.org_id || "HOSPITAL_USER")}`
            );


        const verified =
            data.integrity_status === "VERIFIED";


        if (verified) {

            result.innerHTML = `

                <div class="verification-success">

                    <h2>
                        🟢 RECORD VERIFIED
                    </h2>

                    <p>
                        The current record matches
                        its cryptographic blockchain anchor.
                    </p>


                    <div class="verification-grid">

                        <div class="verification-item">
                            <span>SHA-256 Hash</span>
                            <strong>✓ MATCH</strong>
                        </div>

                        <div class="verification-item">
                            <span>Merkle Proof</span>
                            <strong>
                                ${data.merkle_proof_valid ? "✓ VALID" : "✗ INVALID"}
                            </strong>
                        </div>

                        <div class="verification-item">
                            <span>Blockchain</span>
                            <strong>
                                ${data.blockchain_valid ? "✓ VALID" : "✗ INVALID"}
                            </strong>
                        </div>

                    </div>


                    <p class="hash">
                        Current:
                        ${escapeHtml(data.current_hash)}
                    </p>

                    <p class="hash">
                        Stored:
                        ${escapeHtml(data.stored_hash)}
                    </p>

                </div>

            `;

        } else {

            result.innerHTML = `

                <div class="verification-danger">

                    <h2>
                        🔴 TAMPER DETECTED
                    </h2>

                    <p>
                        The current database record does not
                        match its blockchain integrity anchor.
                    </p>


                    <div class="verification-grid">

                        <div class="verification-item">
                            <span>SHA-256 Hash</span>
                            <strong style="color:#dc2626">
                                ✗ MISMATCH
                            </strong>
                        </div>

                        <div class="verification-item">
                            <span>Merkle Proof</span>
                            <strong style="color:#dc2626">
                                ✗ INVALID
                            </strong>
                        </div>

                        <div class="verification-item">
                            <span>Blockchain</span>
                            <strong>
                                ${data.blockchain_valid ? "✓ VALID" : "✗ INVALID"}
                            </strong>
                        </div>

                    </div>

                </div>

            `;

        }


    } catch (error) {

        result.innerHTML = `
            <div class="verification-danger">
                Verification failed:
                ${escapeHtml(error.message)}
            </div>
        `;

    }
}


/* =========================================================
   TAMPER MESSAGE
========================================================= */

function showTamperMessage(message) {

    const box =
        document.getElementById(
            "tamperMessage"
        );

    box.textContent = message;

    box.classList.remove("hidden");

}


/* =========================================================
   CLINICAL TAMPER
========================================================= */

document
    .getElementById("clinicalTamperBtn")
    .addEventListener(
        "click",
        clinicalTamper
    );


async function clinicalTamper() {

    const encounterId =
        document
            .getElementById("tamperEncounterId")
            .value
            .trim();


    if (!encounterId) {

        showToast(
            "Enter/select an encounter ID."
        );

        return;
    }


    try {

        const data =
            await apiFetch(
                "/api/tamper/clinical",
                {
                    method: "POST",

                    body: JSON.stringify({
                        encounter_id: encounterId,
                        field: "description",
                        new_value:
                            "TAMPERED DIAGNOSIS: SEVERE UNREPORTED CONDITION"
                    })
                }
            );


        showTamperMessage(
            "🚨 Clinical tampering applied. Now click Verify Record."
        );


        showToast(
            "Clinical tampering applied."
        );


    } catch (error) {

        showToast(
            error.message
        );

    }
}


/* =========================================================
   BILLING TAMPER
========================================================= */

document
    .getElementById("billingTamperBtn")
    .addEventListener(
        "click",
        billingTamper
    );


async function billingTamper() {

    const encounterId =
        document
            .getElementById("tamperEncounterId")
            .value
            .trim();


    if (!encounterId) {

        showToast(
            "Enter/select an encounter ID."
        );

        return;
    }


    try {

        const data =
            await apiFetch(
                "/api/tamper/billing",
                {
                    method: "POST",

                    body: JSON.stringify({
                        encounter_id: encounterId,
                        field: "total_claim_cost",
                        new_value: 99999
                    })
                }
            );


        showTamperMessage(
            "🚨 Billing tampering applied. Now click Verify Record."
        );


        showToast(
            "Billing tampering applied."
        );


    } catch (error) {

        showToast(
            error.message
        );

    }
}


/* =========================================================
   RESTORE
========================================================= */

document
    .getElementById("restoreBtn")
    .addEventListener(
        "click",
        restoreRecord
    );


async function restoreRecord() {

    const encounterId =
        document
            .getElementById("tamperEncounterId")
            .value
            .trim();


    if (!encounterId) {

        showToast(
            "Enter/select an encounter ID."
        );

        return;
    }


    try {

        await apiFetch(
            "/api/tamper/restore",
            {
                method: "POST",

                body: JSON.stringify({
                    encounter_id: encounterId
                })
            }
        );


        showTamperMessage(
            "↩ Original record restored. Verify again."
        );


        showToast(
            "Original record restored."
        );


    } catch (error) {

        showToast(
            error.message
        );

    }
}


/* =========================================================
   BLOCKS
========================================================= */

document
    .getElementById("loadBlocksBtn")
    .addEventListener(
        "click",
        loadBlocks
    );


async function loadBlocks() {

    try {

        const data =
            await apiFetch(
                "/api/blockchain/blocks?limit=20&offset=0"
            );


        const blocks =
            data.blocks || [];


        if (!blocks.length) {

            document.getElementById(
                "blocksTable"
            ).innerHTML =
                "No blocks found.";

            return;
        }


        document.getElementById(
            "blocksTable"
        ).innerHTML = `

            <table class="data-table">

                <thead>

                    <tr>

                        <th>Block</th>
                        <th>Transactions</th>
                        <th>Merkle Root</th>
                        <th>Previous Hash</th>
                        <th>Block Hash</th>
                        <th>Nonce</th>

                    </tr>

                </thead>

                <tbody>

                    ${blocks.map(block => `

                        <tr>

                            <td>
                                <strong>
                                    #${escapeHtml(block.block_index)}
                                </strong>
                            </td>

                            <td>
                                ${escapeHtml(block.tx_count)}
                            </td>

                            <td class="hash">
                                ${escapeHtml(block.merkle_root)}
                            </td>

                            <td class="hash">
                                ${escapeHtml(block.previous_hash)}
                            </td>

                            <td class="hash">
                                ${escapeHtml(block.block_hash)}
                            </td>

                            <td>
                                ${escapeHtml(block.nonce)}
                            </td>

                        </tr>

                    `).join("")}

                </tbody>

            </table>

        `;


    } catch (error) {

        document.getElementById(
            "blocksTable"
        ).innerHTML =
            `Unable to load blocks: ${escapeHtml(error.message)}`;

    }
}


/* =========================================================
   AUDIT TRAIL
========================================================= */

document
    .getElementById("refreshAuditBtn")
    .addEventListener(
        "click",
        loadAudit
    );


async function loadAudit() {

    try {

        const data =
            await apiFetch(
                "/api/audit?limit=30"
            );


        const events =
            data.events || [];


        if (!events.length) {

            document.getElementById(
                "auditTable"
            ).innerHTML =
                "No audit events.";

            return;
        }


        document.getElementById(
            "auditTable"
        ).innerHTML = `

            <table class="data-table">

                <thead>

                    <tr>

                        <th>Time</th>
                        <th>Organization</th>
                        <th>Action</th>
                        <th>Patient</th>
                        <th>Status</th>
                        <th>Details</th>

                    </tr>

                </thead>

                <tbody>

                    ${events.map(event => `

                        <tr>

                            <td>
                                ${escapeHtml(event.timestamp)}
                            </td>

                            <td>
                                ${escapeHtml(event.org_id)}
                            </td>

                            <td>
                                <strong>
                                    ${escapeHtml(event.action)}
                                </strong>
                            </td>

                            <td>
                                ${escapeHtml(event.patient_id || "—")}
                            </td>

                            <td class="${
                                event.status === "SUCCESS"
                                ? "valid-badge"
                                : "invalid-badge"
                            }">
                                ${escapeHtml(event.status)}
                            </td>

                            <td>
                                ${escapeHtml(event.details || "")}
                            </td>

                        </tr>

                    `).join("")}

                </tbody>

            </table>

        `;


    } catch (error) {

        document.getElementById(
            "auditTable"
        ).innerHTML =
            `Unable to load audit trail.`;

    }
}


/* =========================================================
   BENCHMARK
========================================================= */

document
    .getElementById("benchmarkBtn")
    .addEventListener(
        "click",
        runBenchmark
    );


async function runBenchmark() {

    const container =
        document.getElementById(
            "benchmarkResults"
        );


    container.innerHTML =
        `<div class="benchmark-placeholder">
            Running benchmarks...
        </div>`;


    try {

        const data =
            await apiFetch(
                "/api/performance/benchmark"
            );


        const results =
            data.benchmarks || {};


        const entries =
            Object.entries(results);


        container.className =
            "benchmark-grid";


        container.innerHTML =
            entries
                .filter(
                    ([key]) =>
                        !key.endsWith("_complexity")
                )
                .map(([key, value]) => {

                    const complexityKey =
                        key + "_complexity";

                    const complexity =
                        results[complexityKey] ||
                        "Complexity available in API";


                    return `

                        <div class="benchmark-card">

                            <h4>
                                ${formatBenchmarkName(key)}
                            </h4>

                            <div class="benchmark-time">

                                ${escapeHtml(value)}

                            </div>

                            <div class="benchmark-complexity">

                                ${escapeHtml(complexity)}

                            </div>

                        </div>

                    `;

                })
                .join("");


    } catch (error) {

        container.innerHTML = `
            <div class="benchmark-placeholder">
                Benchmark failed:
                ${escapeHtml(error.message)}
            </div>
        `;

    }
}


function formatBenchmarkName(name) {

    return name
        .replaceAll("_", " ")
        .replace(/\b\w/g, letter =>
            letter.toUpperCase()
        );

}


/* =========================================================
   AUTO LOGIN FROM SESSION
========================================================= */

const savedUser =
    sessionStorage.getItem(
        "healthcareUser"
    );


if (savedUser) {

    try {

        currentUser =
            JSON.parse(savedUser);

        openDashboard();

    } catch {

        sessionStorage.removeItem(
            "healthcareUser"
        );

    }

}
/* =========================================================
   INSURANCE CLAIMS & BILLING
   ========================================================= */

let selectedClaim = null;

document
    .getElementById("claimSearchBtn")
    ?.addEventListener("click", searchClaims);

async function searchClaims() {
    const patientId = document
        .getElementById("claimPatientId")
        .value
        .trim();

    const claimId = document
        .getElementById("claimIdInput")
        .value
        .trim();

    if (!patientId && !claimId) {
        showToast("Enter a Patient ID or Claim ID.");
        return;
    }

    const list = document.getElementById("claimsList");

    list.innerHTML = `
        <div class="loading">
            Searching insurance claims...
        </div>
    `;

    try {
        const params = new URLSearchParams();

        if (patientId) {
            params.set("patient_id", patientId);
        }

        if (claimId) {
            params.set("claim_id", claimId);
        }

        params.set("limit", "50");

        const data = await apiFetch(
            `/api/claims/search?${params.toString()}`
        );

        const claims = Array.isArray(data)
            ? data
            : (data.claims || data.results || []);

        if (!claims.length) {
            list.innerHTML = `
                <div class="empty-state">
                    No insurance claims found.
                </div>
            `;

            document
                .getElementById("claimDetails")
                .classList.add("hidden");

            return;
        }

        list.innerHTML = claims.map((claim, index) => `
            <div
                class="claim-card"
                data-claim-index="${index}"
            >
                <div class="claim-card-main">
                    <strong>
                        Claim ${escapeHtml(claim.id || claim.claim_id || "Unknown")}
                    </strong>

                    <span>
                        Patient:
                        ${escapeHtml(claim.patient_id || "Unknown")}
                    </span>

                    <span>
                        Status:
                        ${escapeHtml(claim.status || "Unknown")}
                    </span>

                    <span>
                        Amount:
                        ₹${escapeHtml(
                            String(claim.total_claim_cost ?? "0")
                        )}
                    </span>
                </div>

                <button
                    class="outline-btn claim-select-btn"
                    data-claim-index="${index}">
                    View Claim
                </button>
            </div>
        `).join("");

        list.querySelectorAll(".claim-select-btn")
            .forEach(button => {
                button.addEventListener("click", () => {
                    const index = Number(
                        button.dataset.claimIndex
                    );

                    selectClaim(claims[index]);
                });
            });

        showToast(`${claims.length} claim(s) found.`);

    } catch (error) {
        list.innerHTML = `
            <div class="empty-state">
                Claim search failed:
                ${escapeHtml(error.message)}
            </div>
        `;

        showToast(error.message);
    }
}


function selectClaim(claim) {
    selectedClaim = claim;

    const claimId =
        claim.id ||
        claim.claim_id ||
        "Unknown Claim";

    document.getElementById("claimDetails")
        .classList.remove("hidden");

    document.getElementById("selectedClaimTitle")
        .textContent = claimId;

    document.getElementById("claimInfo").innerHTML = `
        <div class="verification-grid">

            <div class="verification-item">
                <span>Patient ID</span>
                <strong>
                    ${escapeHtml(claim.patient_id || "—")}
                </strong>
            </div>

            <div class="verification-item">
                <span>Encounter ID</span>
                <strong>
                    ${escapeHtml(claim.encounter_id || "—")}
                </strong>
            </div>

            <div class="verification-item">
                <span>Status</span>
                <strong>
                    ${escapeHtml(claim.status || "—")}
                </strong>
            </div>

            <div class="verification-item">
                <span>Total Claim Cost</span>
                <strong>
                    ₹${escapeHtml(
                        String(claim.total_claim_cost ?? "0")
                    )}
                </strong>
            </div>

            <div class="verification-item">
                <span>Payer Coverage</span>
                <strong>
                    ₹${escapeHtml(
                        String(claim.payer_coverage ?? "0")
                    )}
                </strong>
            </div>

            <div class="verification-item">
                <span>Diagnosis Code</span>
                <strong>
                    ${escapeHtml(claim.diagnosis_code || "—")}
                </strong>
            </div>

            <div class="verification-item">
                <span>Procedure Code</span>
                <strong>
                    ${escapeHtml(claim.procedure_code || "—")}
                </strong>
            </div>

            <div class="verification-item">
                <span>Hospital</span>
                <strong>
                    ${escapeHtml(claim.org_name || "—")}
                </strong>
            </div>

        </div>
    `;

    const verification =
        document.getElementById("claimVerification");

    verification.classList.add("hidden");
    verification.innerHTML = "";

    document
        .getElementById("verifyClaimBtn")
        .onclick = verifySelectedClaim;

    showToast("Claim selected.");
}


async function verifySelectedClaim() {
    if (!selectedClaim) {
        showToast("Select a claim first.");
        return;
    }

    const claimId =
        selectedClaim.id ||
        selectedClaim.claim_id;

    if (!claimId) {
        showToast("Claim ID is missing.");
        return;
    }

    const verification =
        document.getElementById("claimVerification");

    verification.classList.remove("hidden");

    verification.innerHTML = `
        <div class="loading">
            Verifying claim integrity...
        </div>
    `;

    try {
        const payer =
            currentUser?.org_id ||
            "INSURANCE_USER";

        const data = await apiFetch(
            `/api/claims/${encodeURIComponent(claimId)}/verify?verifying_payer=${encodeURIComponent(payer)}`
        );

        const verified =
            data.billing_integrity_verified === true ||
            data.integrity_status === "VERIFIED";

        if (verified) {

            verification.innerHTML = `
                <div class="verification-success">
                    <h3>🛡️ CLAIM VERIFIED</h3>

                    <p>
                        The billing claim matches its
                        cryptographic blockchain anchor.
                    </p>

                    <div class="verification-grid">

                        <div class="verification-item">
                            <span>Billing Integrity</span>
                            <strong style="color:#16a34a">
                                ✓ VERIFIED
                            </strong>
                        </div>

                        <div class="verification-item">
                            <span>SHA-256</span>
                            <strong style="color:#16a34a">
                                ✓ MATCH
                            </strong>
                        </div>

                        <div class="verification-item">
                            <span>Merkle Proof</span>
                            <strong style="color:#16a34a">
                                ✓ VALID
                            </strong>
                        </div>

                        <div class="verification-item">
                            <span>Blockchain</span>
                            <strong style="color:#16a34a">
                                ✓ VALID
                            </strong>
                        </div>

                    </div>
                </div>
            `;

        } else {

            verification.innerHTML = `
                <div class="verification-danger">
                    <h3>⚠️ BILLING TAMPER DETECTED</h3>

                    <p>
                        The current claim data does not match
                        its cryptographic blockchain anchor.
                    </p>

                    <div class="verification-grid">

                        <div class="verification-item">
                            <span>Billing Integrity</span>
                            <strong style="color:#dc2626">
                                ✗ MISMATCH
                            </strong>
                        </div>

                        <div class="verification-item">
                            <span>SHA-256</span>
                            <strong style="color:#dc2626">
                                ✗ MISMATCH
                            </strong>
                        </div>

                        <div class="verification-item">
                            <span>Merkle Proof</span>
                            <strong style="color:#dc2626">
                                ✗ INVALID
                            </strong>
                        </div>

                        <div class="verification-item">
                            <span>Blockchain</span>
                            <strong style="color:#16a34a">
                                ✓ VALID
                            </strong>
                        </div>

                    </div>
                </div>
            `;
        }

        showToast(
            verified
                ? "Claim integrity verified."
                : "Billing tampering detected."
        );

    } catch (error) {

        verification.innerHTML = `
            <div class="verification-danger">
                Claim verification failed:
                ${escapeHtml(error.message)}
            </div>
        `;

        showToast(error.message);
    }
}

/* =========================================================
   DATA STRUCTURE VISUALIZER
   LIVE MERKLE TREE + LINKED BLOCKCHAIN
========================================================= */

const DS_VISUALIZER_LATEST_BLOCK = 126;
const DS_MIN_MERKLE_LEAVES = 50;


/* ---------------------------------------------------------
   SHA-256
--------------------------------------------------------- */

async function dsSha256Hex(text) {

    const data =
        new TextEncoder().encode(text);

    const hashBuffer =
        await window.crypto.subtle.digest(
            "SHA-256",
            data
        );

    return Array.from(
        new Uint8Array(hashBuffer)
    )
        .map(
            byte =>
                byte
                    .toString(16)
                    .padStart(2, "0")
        )
        .join("");
}


/* ---------------------------------------------------------
   Escape HTML
--------------------------------------------------------- */

function dsEscapeHtml(value) {

    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


/* ---------------------------------------------------------
   Short hash
--------------------------------------------------------- */

function dsShortHash(hash) {

    if (!hash) {
        return "—";
    }

    if (hash.length <= 18) {
        return hash;
    }

    return (
        hash.substring(0, 10) +
        "..." +
        hash.substring(hash.length - 8)
    );
}


/* ---------------------------------------------------------
   Build REAL Merkle Tree
--------------------------------------------------------- */

async function dsBuildMerkleLevels(
    leaves
) {

    if (
        !leaves ||
        leaves.length === 0
    ) {
        return [];
    }

    let currentLevel =
        [...leaves];

    const levels = [
        currentLevel
    ];

    while (
        currentLevel.length > 1
    ) {

        const nextLevel = [];

        for (
            let i = 0;
            i < currentLevel.length;
            i += 2
        ) {

            const left =
                currentLevel[i];

            const right =
                currentLevel[i + 1] ||
                currentLevel[i];

            const parentHash =
                await dsSha256Hex(
                    left + right
                );

            nextLevel.push(
                parentHash
            );
        }

        currentLevel =
            nextLevel;

        levels.push(
            currentLevel
        );
    }

    return levels;
}


/* ---------------------------------------------------------
   Find a block containing at least 50 transactions
--------------------------------------------------------- */

async function dsFindDemoBlock() {

    for (
        let blockIndex = 1;
        blockIndex <=
        DS_VISUALIZER_LATEST_BLOCK;
        blockIndex++
    ) {

        try {

            const block =
                await apiFetch(
                    `/api/blockchain/blocks/${blockIndex}`
                );

            const transactions =
                block.transactions || [];

            if (
                transactions.length >=
                DS_MIN_MERKLE_LEAVES
            ) {

                return block;
            }

        } catch (error) {

            console.warn(
                "Could not inspect block",
                blockIndex,
                error
            );
        }
    }

    return null;
}


/* ---------------------------------------------------------
   Populate block dropdown
--------------------------------------------------------- */

function dsPopulateBlockSelector(
    defaultBlockIndex
) {

    const selector =
        document.getElementById(
            "visualizerBlockSelect"
        );

    if (!selector) {
        return;
    }

    selector.innerHTML = "";

    for (
        let i =
            DS_VISUALIZER_LATEST_BLOCK;
        i >= 0;
        i--
    ) {

        const option =
            document.createElement(
                "option"
            );

        option.value = i;

        option.textContent =
            `Block #${i}`;

        if (
            i ===
            defaultBlockIndex
        ) {

            option.selected = true;
        }

        selector.appendChild(
            option
        );
    }
}


/* ---------------------------------------------------------
   Render Merkle Tree
--------------------------------------------------------- */

function dsRenderMerkleTree(levels, transactions) {
    const container =
        document.getElementById("merkleTreeVisualization");

    if (!container) return;

    if (!levels || !levels.length) {
        container.innerHTML = `
            <div class="ds-empty-state">
                No Merkle tree data available.
            </div>
        `;
        return;
    }

    /*
     * levels[0] = leaf hashes
     * levels[last] = Merkle root
     *
     * We calculate positions from the leaves upward,
     * then draw the tree from root to leaves.
     */

    const leafCount = levels[0].length;

    // Horizontal spacing between leaf nodes.
    // 500 leaves => wide scrollable tree.
    const spacing = leafCount >= 100 ? 30 : 70;

    const nodeRadius = leafCount >= 100 ? 5 : 12;

    const levelHeight = 85;
    const topPadding = 55;
    const bottomPadding = 65;

    const svgWidth =
        Math.max(
            1100,
            leafCount * spacing
        );

    const svgHeight =
        topPadding +
        (levels.length - 1) * levelHeight +
        bottomPadding;

    /*
     * ---------------------------------------------------------
     * Calculate X positions for every node.
     * ---------------------------------------------------------
     */

    const positions = [];

    // Leaf positions
    positions[0] = levels[0].map(
        (_, index) =>
            (index + 0.5) * spacing
    );

    // Parent positions
    for (let level = 1; level < levels.length; level++) {
        const previousPositions =
            positions[level - 1];

        positions[level] =
            levels[level].map(
                (_, index) => {

                    const leftIndex =
                        index * 2;

                    const rightIndex =
                        Math.min(
                            leftIndex + 1,
                            previousPositions.length - 1
                        );

                    const leftX =
                        previousPositions[leftIndex];

                    const rightX =
                        previousPositions[rightIndex];

                    return (
                        (leftX + rightX) / 2
                    );
                }
            );
    }

    /*
     * ---------------------------------------------------------
     * Build SVG
     * ---------------------------------------------------------
     */

    let svg = `
        <svg
            class="ds-merkle-svg"
            width="${svgWidth}"
            height="${svgHeight}"
            viewBox="0 0 ${svgWidth} ${svgHeight}"
            xmlns="http://www.w3.org/2000/svg"
        >
    `;

    /*
     * ---------------------------------------------------------
     * Draw connecting lines first.
     * ---------------------------------------------------------
     */

    for (
        let level = levels.length - 1;
        level > 0;
        level--
    ) {
        const parentY =
            topPadding +
            (levels.length - 1 - level) *
                levelHeight;

        const childY =
            parentY + levelHeight;

        positions[level].forEach(
            (parentX, parentIndex) => {

                const leftIndex =
                    parentIndex * 2;

                const rightIndex =
                    Math.min(
                        leftIndex + 1,
                        positions[level - 1].length - 1
                    );

                const leftX =
                    positions[level - 1][leftIndex];

                const rightX =
                    positions[level - 1][rightIndex];

                svg += `
                    <line
                        class="ds-merkle-branch"
                        x1="${parentX}"
                        y1="${parentY + nodeRadius}"
                        x2="${leftX}"
                        y2="${childY - nodeRadius}"
                    />
                `;

                if (rightIndex !== leftIndex) {
                    svg += `
                        <line
                            class="ds-merkle-branch"
                            x1="${parentX}"
                            y1="${parentY + nodeRadius}"
                            x2="${rightX}"
                            y2="${childY - nodeRadius}"
                        />
                    `;
                }
            }
        );
    }

    /*
     * ---------------------------------------------------------
     * Draw nodes.
     * ---------------------------------------------------------
     */

    for (
        let level = levels.length - 1;
        level >= 0;
        level--
    ) {
        const visualLevel =
            levels.length - 1 - level;

        const y =
            topPadding +
            visualLevel * levelHeight;

        const isRoot =
            level === levels.length - 1;

        const isLeaf =
            level === 0;

        const hashes =
            levels[level];

        hashes.forEach(
            (hash, index) => {

                const x =
                    positions[level][index];

                let nodeClass =
                    "ds-merkle-svg-node";

                if (isRoot) {
                    nodeClass +=
                        " ds-merkle-svg-root";
                } else if (isLeaf) {
                    nodeClass +=
                        " ds-merkle-svg-leaf";
                } else {
                    nodeClass +=
                        " ds-merkle-svg-parent";
                }

                /*
                 * Find the corresponding transaction
                 * for leaf nodes.
                 */
                const tx =
                    isLeaf &&
                    transactions &&
                    transactions[index]
                        ? transactions[index]
                        : null;

                const recordId =
                    tx?.record_id || "";

                const txId =
                    tx?.tx_id || "";

                svg += `
                    <g
                        class="${nodeClass}"
                        transform="translate(${x}, ${y})"
                    >
                        <title>
                            ${isRoot
                                ? "MERKLE ROOT"
                                : isLeaf
                                    ? `Leaf ${index + 1}
Record: ${recordId}
Transaction: ${txId}
Hash: ${hash}`
                                    : `SHA-256 Parent Hash
Hash: ${hash}`
                            }
                        </title>

                        <circle
                            cx="0"
                            cy="0"
                            r="${nodeRadius}"
                        />
                `;

                /*
                 * Labels:
                 *
                 * Root gets a full label.
                 * Upper levels get short labels.
                 * Leaf nodes remain compact because
                 * there may be 500 of them.
                 */

                if (isRoot) {

                    svg += `
                        <text
                            class="ds-merkle-svg-root-label"
                            x="0"
                            y="-18"
                        >
                            MERKLE ROOT
                        </text>

                        <text
                            class="ds-merkle-svg-hash"
                            x="0"
                            y="27"
                        >
                            ${dsShortHash(hash)}
                        </text>
                    `;

                } else if (
                    level >= levels.length - 4
                ) {

                    svg += `
                        <text
                            class="ds-merkle-svg-level-label"
                            x="0"
                            y="-14"
                        >
                            ${dsShortHash(hash)}
                        </text>
                    `;

                } else if (
                    isLeaf &&
                    index < 50
                ) {

                    svg += `
                        <text
                            class="ds-merkle-svg-leaf-label"
                            x="0"
                            y="18"
                        >
                            ${index + 1}
                        </text>
                    `;
                }

                svg += `
                    </g>
                `;
            }
        );
    }

    /*
     * ---------------------------------------------------------
     * Level labels on left side.
     * ---------------------------------------------------------
     */

    for (
        let level = levels.length - 1;
        level >= 0;
        level--
    ) {
        const visualLevel =
            levels.length - 1 - level;

        const y =
            topPadding +
            visualLevel * levelHeight;

        let label;

        if (level === levels.length - 1) {
            label = "ROOT";
        } else if (level === 0) {
            label = `LEAVES (${levels[0].length})`;
        } else {
            label = `LEVEL ${level}`;
        }

        svg += `
            <text
                class="ds-merkle-svg-side-label"
                x="10"
                y="${y + 4}"
            >
                ${label}
            </text>
        `;
    }

    svg += `
        </svg>

        <div class="ds-merkle-tree-caption">
            <span>● Parent / Hash Node</span>
            <span>● Leaf = SHA-256 Transaction Hash</span>
            <span>● Hover a leaf to inspect its record</span>
            <span>● ${leafCount} real transaction leaves</span>
        </div>
    `;

    container.innerHTML = svg;
}

/* ---------------------------------------------------------
   Render blockchain blocks
--------------------------------------------------------- */

function dsRenderBlockchainChain(
    blocks
) {

    const container =
        document.getElementById(
            "blockchainChainVisualization"
        );

    if (!container) {
        return;
    }

    let html = "";


    blocks.forEach(
        (block, index) => {

            html += `

                <div class="ds-chain-block">

                    <div class="ds-chain-block-header">

                        <strong>
                            Block #${block.block_index}
                        </strong>

                        <span class="valid-badge">
                            LIVE
                        </span>

                    </div>


                    <div class="ds-chain-field">

                        <span>
                            Previous Hash
                        </span>

                        <code>
                            ${dsEscapeHtml(
                                block.previous_hash
                            )}
                        </code>

                    </div>


                    <div class="ds-chain-field">

                        <span>
                            Merkle Root
                        </span>

                        <code>
                            ${dsEscapeHtml(
                                block.merkle_root
                            )}
                        </code>

                    </div>


                    <div class="ds-chain-field">

                        <span>
                            Block Hash
                        </span>

                        <code>
                            ${dsEscapeHtml(
                                block.block_hash
                            )}
                        </code>

                    </div>


                    <div class="ds-chain-meta">

                        <span>
                            TX:
                            ${block.tx_count}
                        </span>

                        <span>
                            Nonce:
                            ${block.nonce}
                        </span>

                    </div>

                </div>
            `;


            if (
                index <
                blocks.length - 1
            ) {

                html += `

                    <div class="ds-chain-arrow">

                        ↓

                        <span>
                            previous_hash
                        </span>

                    </div>
                `;
            }
        }
    );


    container.innerHTML =
        html;
}


/* ---------------------------------------------------------
   Load selected block
--------------------------------------------------------- */

async function loadDataStructureVisualizer(
    blockIndex
) {

    try {

        const block =
            await apiFetch(
                `/api/blockchain/blocks/${blockIndex}`
            );
	
        /*
         * Update total blockchain blocks.
         */

        const totalBlocks =
            document.getElementById(
                "visualizerTotalBlocks"
            );

        if (totalBlocks) {

            totalBlocks.textContent =
                DS_VISUALIZER_LATEST_BLOCK + 1;
        }

        const transactions =
            block.transactions || [];


        /*
         * Update summary.
         */

        const txCount =
            document.getElementById(
                "visualizerTxCount"
            );

        const treeHeight =
            document.getElementById(
                "visualizerTreeHeight"
            );

        const merkleRoot =
            document.getElementById(
                "visualizerMerkleRoot"
            );

        const selectedBlock =
            document.getElementById(
                "visualizerSelectedBlock"
            );

        const nonce =
            document.getElementById(
                "visualizerNonce"
            );


        if (txCount) {

            txCount.textContent =
                transactions.length;
        }


        if (selectedBlock) {

            selectedBlock.textContent =
                `#${block.block_index}`;
        }


        if (nonce) {

            nonce.textContent =
                block.nonce;
        }


        /*
         * Real transaction hashes.
         */

        const leaves =
            transactions
                .map(
                    transaction =>
                        transaction.record_hash
                )
                .filter(Boolean);


        /*
         * Build actual Merkle tree.
         */

        const levels =
            await dsBuildMerkleLevels(
                leaves
            );


        if (treeHeight) {

            treeHeight.textContent =
                levels.length;
        }


        if (merkleRoot) {

            merkleRoot.textContent =
                block.merkle_root;
        }


        /*
         * Calculate root.
         */

        const calculatedRoot =
            levels.length
                ? levels[
                    levels.length - 1
                ][0]
                : null;


        const rootMatches =
            calculatedRoot ===
            block.merkle_root;


        /*
         * Render tree.
         */

        dsRenderMerkleTree(
            levels,
            transactions
        );


        /*
         * Selected block details.
         */

        const blockDetails =
            document.getElementById(
                "selectedBlockVisualization"
            );


        if (blockDetails) {

            blockDetails.innerHTML = `

                <div class="ds-selected-block-card">

                    <div class="ds-selected-block-title">

                        Block #${block.block_index}

                    </div>


                    <div class="ds-selected-field">

                        <span>
                            Block Hash
                        </span>

                        <code>
                            ${dsEscapeHtml(
                                block.block_hash
                            )}
                        </code>

                    </div>


                    <div class="ds-selected-field">

                        <span>
                            Previous Hash
                        </span>

                        <code>
                            ${dsEscapeHtml(
                                block.previous_hash
                            )}
                        </code>

                    </div>


                    <div class="ds-selected-field">

                        <span>
                            Merkle Root
                        </span>

                        <code>
                            ${dsEscapeHtml(
                                block.merkle_root
                            )}
                        </code>

                    </div>


                    <div class="ds-selected-field">

                        <span>
                            Calculated Root
                        </span>

                        <code>
                            ${dsEscapeHtml(
                                calculatedRoot
                            )}
                        </code>

                    </div>


                    <div class="ds-integrity-result">

                        ${
                            rootMatches
                                ? `
                                    <span class="valid-badge">
                                        ✓ MERKLE ROOT VERIFIED
                                    </span>
                                `
                                : `
                                    <span class="invalid-badge">
                                        ✕ MERKLE ROOT MISMATCH
                                    </span>
                                `
                        }

                    </div>

                </div>
            `;
        }


        /*
         * Load selected block + two previous blocks.
         */

        const chainBlocks = [];


        for (
            let i =
                block.block_index;
            i >=
                Math.max(
                    0,
                    block.block_index - 2
                );
            i--
        ) {

            try {

                const chainBlock =
                    await apiFetch(
                        `/api/blockchain/blocks/${i}`
                    );

                chainBlocks.push(
                    chainBlock
                );

            } catch (error) {

                console.warn(
                    "Unable to load block",
                    i
                );
            }
        }


        dsRenderBlockchainChain(
            chainBlocks
        );


        /*
         * Verify previous hash link.
         */

        const previousHashBox =
            document.getElementById(
                "previousHashVisualization"
            );


        if (previousHashBox) {

            if (
                block.block_index === 0
            ) {

                previousHashBox.innerHTML = `

                    <div class="ds-link-valid">

                        Genesis Block —
                        no previous block

                    </div>
                `;

            } else {

                const previousBlock =
                    chainBlocks.find(
                        item =>
                            item.block_index ===
                            block.block_index - 1
                    );


                const linkValid =
                    previousBlock &&
                    previousBlock.block_hash ===
                    block.previous_hash;


                previousHashBox.innerHTML = `

                    <div class="ds-link-card">

                        <strong>
                            Block #${
                                block.block_index - 1
                            }
                        </strong>

                        <span>
                            ↓ previous_hash ↓
                        </span>

                        <strong>
                            Block #${
                                block.block_index
                            }
                        </strong>


                        <div class="ds-link-hash">

                            Previous block hash:

                            <code>
                                ${dsEscapeHtml(
                                    previousBlock
                                        ?.block_hash ||
                                    "Unavailable"
                                )}
                            </code>

                        </div>


                        <div class="ds-link-hash">

                            Current block previous_hash:

                            <code>
                                ${dsEscapeHtml(
                                    block.previous_hash
                                )}
                            </code>

                        </div>


                        ${
                            linkValid
                                ? `
                                    <span class="valid-badge">
                                        ✓ HASH LINK VALID
                                    </span>
                                `
                                : `
                                    <span class="invalid-badge">
                                        ✕ HASH LINK BROKEN
                                    </span>
                                `
                        }

                    </div>
                `;
            }
        }


    } catch (error) {

        console.error(
            "Data Structure Visualizer error:",
            error
        );

        const tree =
            document.getElementById(
                "merkleTreeVisualization"
            );

        if (tree) {

            tree.innerHTML = `

                <div class="ds-empty-state">

                    Unable to load blockchain data.

                    <br>

                    ${dsEscapeHtml(
                        error.message
                    )}

                </div>
            `;
        }
    }
}


/* ---------------------------------------------------------
   Initialize visualizer
--------------------------------------------------------- */

async function initializeDataStructureVisualizer() {

    try {

        /*
         * Use Block #122 as the default DSA demonstration
         * block because it contains 500 real transactions.
         */

        const demoBlockIndex = 122;


        /*
         * Populate dropdown with all available blocks
         * and select Block #122.
         */

        dsPopulateBlockSelector(
            demoBlockIndex
        );


        /*
         * Load the exact same block into:
         *
         * 1. Merkle Tree
         * 2. Selected Block details
         * 3. Blockchain visualization
         * 4. Previous-hash verification
         */

        await loadDataStructureVisualizer(
            demoBlockIndex
        );


    } catch (error) {

        console.error(
            "Visualizer initialization failed:",
            error
        );


        /*
         * Fallback to the latest block.
         */

        dsPopulateBlockSelector(
            DS_VISUALIZER_LATEST_BLOCK
        );


        await loadDataStructureVisualizer(
            DS_VISUALIZER_LATEST_BLOCK
        );
    }
}

/* ---------------------------------------------------------
   Dropdown
--------------------------------------------------------- */

const dsBlockSelector =
    document.getElementById(
        "visualizerBlockSelect"
    );


if (dsBlockSelector) {

    dsBlockSelector.addEventListener(
        "change",
        async () => {

            const selectedBlock =
                Number(
                    dsBlockSelector.value
                );

            await loadDataStructureVisualizer(
                selectedBlock
            );
        }
    );
}


/* ---------------------------------------------------------
   Refresh
--------------------------------------------------------- */

const dsRefreshButton =
    document.getElementById(
        "refreshVisualizerBtn"
    );


if (dsRefreshButton) {

    dsRefreshButton.addEventListener(
        "click",
        async () => {

            const selectedBlock =
                Number(
                    dsBlockSelector?.value ||
                    126
                );

            await loadDataStructureVisualizer(
                selectedBlock
            );
        }
    );
}


/* ---------------------------------------------------------
   Start
--------------------------------------------------------- */

if (
    document.getElementById(
        "dsVisualizerPanel"
    )
) {

    initializeDataStructureVisualizer();
}