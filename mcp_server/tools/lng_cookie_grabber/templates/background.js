const RUN_PLUGIN_BUTTON_ID = "run-cookies-plugin";
const PLUGIN_STATUS_CLASS = "status-cookies-plugin";

const MESSAGE__STEP1__TO_PLUGIN__START_FETCH = "start-fetch";
const MESSAGE__STEP2__TO_PLUGIN__SAVE_COOKIES = "save-page-cookies";
const MESSAGE__STEP3__TO_MAIN_PAGE__PROCESS_RESULT = "process-result";

let emergencySocket = null;
let expectedPluginVersion = null;
let PLUGIN_VERSION = "5"; // please also check WebSocketConfig
let listPortals = []; // will be loaded from DOM
let sessionId = ""; // will be loaded from DOM

async function processInjection() {
    console.log("#30 Processing injection of the plugin elements.");

// <OTHER_PAGES_INJECTION>

    console.log("#40 Injection of the plugin elements is done.");
}

if (typeof chrome.commands !== 'undefined') {

    // ------------------------ plugin background part ------------------------

    let urls = [];
    let sitesCookies = [];
    let originalTabId = null;

    chrome.runtime.onMessage.addListener(function (message, sender) {
        console.log("#4 Start fetching cookies. Setting all urls and starting opening new tabs.");
        if (message.command === MESSAGE__STEP1__TO_PLUGIN__START_FETCH) {
            originalTabId = sender.tab.id;
            urls = message.portals
            fetchNext();
        }
    });

    function fetchNext() {
        // get next URL
        let pageUrl = urls.shift();

        console.log("#5 Opening new tab with #plugin hash for the  URL: " + pageUrl);
        chrome.tabs.create({ url: pageUrl, active: false });
    }

    chrome.runtime.onMessage.addListener(function (message, sender) {
        if (message.command !== MESSAGE__STEP2__TO_PLUGIN__SAVE_COOKIES) return;

        console.log("#7 Saving all cookies from the page.");
        chrome.cookies.getAll({
            domain: message.domain
        }, function (cookies) {
            console.log("#8 Cookies data for the page with the page url: " + message.href);
            let cookieData = [];
            for (var i = 0; i < cookies.length; i++) {
                cookieData.push(cookies[i].name + "=" + cookies[i].value);
            }
            sitesCookies.push({ cookies: cookieData, href: message.href });

            console.log("#8.2 Close the tab we opened.");
            closeTab(sender);

            if (urls && urls.length) {
                console.log("#10 We have more urls to process, open the next tab.");
                fetchNext();
            } else {
                console.log("#11 Processed all urls, send the result to the main page.");
                chrome.tabs.sendMessage(originalTabId, {
                    command: MESSAGE__STEP3__TO_MAIN_PAGE__PROCESS_RESULT,
                    data: sitesCookies
                });

                console.log("#11.2 Clear the cookies data.");
                urls = [];
                sitesCookies = [];
            }
        });
        return true;
    });

    function closeTab(sender) {
        console.log("#9 Closing the tab we opened.");
        chrome.tabs.remove(sender.tab.id);
    }

} else {

    // ------------------------ content script part ------------------------

    let triggeredByPlugin = window.location.href.includes("#plugin");

    if (triggeredByPlugin) {

        // ------ this part will be executed in the context of the page opened by the plugin (for cookie fetching)

        window.addEventListener('load', function () {
            console.log("#6 Page is loaded with '#plugin' hash. " +
                "Sending a message to the background script to save the cookies.");
            let domain = window.location.hostname;
            let href = window.location.href;
            chrome.runtime.sendMessage({ command: MESSAGE__STEP2__TO_PLUGIN__SAVE_COOKIES, domain, href });
        });

    } else {
        // ------ this part is executed in the context of the main page

        function statusElements() {
            let elements = document.getElementsByClassName(PLUGIN_STATUS_CLASS);
            return Array.from(elements);
        }

        function getStatusElement() {
            return document.getElementsByClassName(PLUGIN_STATUS_CLASS)[0];
        }

        function changeStatus(elements, message, color) {
            elements.forEach(element => {
                element.innerHTML = message;
                element.style.backgroundColor = color;
            });
        }

        function updateStatus() {
            let element = getStatusElement();
            if (!element) return;
            
            let isConnected = !!emergencySocket
                && !!emergencySocket.readyState
                && emergencySocket.readyState === WebSocket.OPEN;
            let isWrongVersion = expectedPluginVersion != null && expectedPluginVersion !== PLUGIN_VERSION;

            if (isWrongVersion) {
                changeStatus([element], "[please run `add` command, download new version of plugin and reinstall it]", "#ff7137");
            } else {
                if (isConnected) {
                    changeStatus([element], "[plugin connected]", "#ac59e4");
                } else {
                    changeStatus([element], "[plugin installed]", "#75df78");
                }
            }
        }

        function parameter(name) {
            const url = new URLSearchParams(window.location.search);
            const value = url.get(name);
            return value ? value : null;
        }

        // this will open websocket channel in case you need to send cookies in an emergency
        function setupWs(onMessage) {
            console.log("#2.5 Opening websocket connection.");
            emergencySocket = "opening";
            let url = `{{WS_SERVER_URL}}?sessionId=${sessionId}`;
            console.log(`#2.5.1 WebSocket URL: ${url}`);
            let socket = new WebSocket(url);

            socket.onopen = function(e) {
                console.log(`#2.6 WebSocket connection established to: ${url}`);
                emergencySocket = socket;
                updateStatus();
            };

            socket.onmessage = function(event) {
                console.log(`#16.1 Data received from server: ${event.data}`);

                if (event.data.includes("Ping")) {
                    expectedPluginVersion = event.data.split("Version: ")[1];
                    updateStatus();

                    socket.send("Pong");
                    return;
                }

                if (event.data === "GetCookies") {
                    console.log(`#16.2 Something went wrong on server with cookies. Server requested cookies. Start fetching.`);
                    if (!!onMessage) {
                        onMessage(event.data);
                    }
                }
            };

            function reconnect() {
                console.log(`#19 Reconnecting WebSocket to ${url} in 5 seconds...`);
                setTimeout(() => {
                    setupWs(onMessage);
                }, 5000);
            }

            socket.onclose = function(event) {
                if (event.wasClean) {
                    console.log(`#18.1 WebSocket connection closed cleanly. Code: ${event.code}, Reason: ${event.reason}`);
                } else {
                    console.log(`#18.2 WebSocket connection died. Code: ${event.code}`);
                    socket.close();
                }
                emergencySocket = null;
                socket = null;

                updateStatus();

                reconnect();
            };

            socket.onerror = function(error) {
                emergencySocket = null;
                console.error(`#20 Websocket error: ${!!error.message ? error.message : "unknown"}`);
            };
        }

        function startFetchingCookies() {
            console.log("#12 Sending a message to the background script to start fetching cookies (first - open new tabs).");
            chrome.runtime.sendMessage({ command: MESSAGE__STEP1__TO_PLUGIN__START_FETCH, portals: listPortals });
        }

        function setupRunPluginClick(element) {
            if (!element) return;

            console.log("#3 Adding event listener on click to the `RUN_PLUGIN_BUTTON_ID` element. " +
                "It will start fetching procedure.");
            element.addEventListener('click', function () {
                startFetchingCookies();
            });
        }

        function initWebsocket() {
            if (!emergencySocket) {
                console.log("#2.4 Initializing WebSocket connection for emergency cookie sending...");
                setupWs(function(data) {
                    console.log("#17 Emergency WebSocket request received. Server requested cookies. Starting fetch...");
                    startFetchingCookies();
                });
            }
        }

        function setupPluginStatus(element) {
            if (!element) return;

            console.log("#2.3 Setting up plugin status element.");
            updateStatus();

            initWebsocket();
        }

        function changeTempStatus(status, color) {
            changeStatus(statusElements(), status, color);
            setTimeout(() => {
                updateStatus();
            }, 10000);
        }

        function processChatPage() {
            console.log("#1 This is the main page we will work with.");

            console.log(`#2 Trying to find the ${RUN_PLUGIN_BUTTON_ID} element and add click event listener.`);
            setupRunPluginClick(document.getElementById(RUN_PLUGIN_BUTTON_ID));

            console.log(`#2.2 Trying to find the ${PLUGIN_STATUS_CLASS} element and updating plugin status.`);
            let statusElement = getStatusElement();
            setupPluginStatus(statusElement);
        }

        function extractDataFromDOM() {
            // Extract session ID and portals from DOM
            const sessionElement = document.getElementById('session-id');
            const portalsElement = document.getElementById('portals');
            
            if (sessionElement) {
                sessionId = sessionElement.textContent.trim();
                console.log("#0.1 Extracted sessionId from DOM:", sessionId);
            }
            
            if (portalsElement) {
                try {
                    listPortals = JSON.parse(portalsElement.textContent.trim());
                    console.log("#0.2 Extracted portals from DOM:", listPortals);
                } catch (e) {
                    console.error("#0.3 Failed to parse portals from DOM:", e);
                }
            }
        }

        // during the page load, we try to find the `RUN_PLUGIN_BUTTON_ID` element and add event listener on click
        // of something changes in the DOM, we check if the element is added and add event listener
        window.addEventListener('load', async function () {
            // Extract data from DOM first
            extractDataFromDOM();
            
            // For status page, also setup plugin status
            if (window.location.href.includes("{{SERVER_URL}}")) {
                console.log("#0.4 This is status page, setting up plugin status.");
                
                processChatPage();
                updateStatus();
            }

            await processInjection();
        });

        chrome.runtime.onMessage.addListener(function (message) {
            if (message.command !== MESSAGE__STEP3__TO_MAIN_PAGE__PROCESS_RESULT) return;
            if (!message.data) return;

            console.log("#13 Processing the result (all cookies) from the plugin.");
            let result = message.data.map(data => {
                let domainOnly = `https://${data.href.split("/")[2]}`;
                return "GET " + domainOnly + " HTTP/3\n" +
                    "Cookie: " + data.cookies.join("; ");
            }).join("\n");

            // if result not contains all of listPortals, show alert
            let resultArray = result.split("\n");
            let foundAll = false;
            for (let i = 0; i < listPortals.length; i++) {
                let found = false;
                for (let j = 0; j < resultArray.length; j++) {
                    let url = new URL(listPortals[i]).hostname;
                    if (resultArray[j].includes(url)) {
                        found = true;
                        break;
                    }
                }
                if (!found) {
                    foundAll = false;
                    break;
                }
                foundAll = true;
            }
            if (foundAll) {
                changeTempStatus("[cookies were sent by plugin]", "#dfda75");
                console.log("#15.1 Sending the result to the server.");
                emergencySocket.send(result);
            } else {
                alert("Not all cookies were sent. Try login manually. And send cookies again.");
                console.log("#15.2 Not all cookies were sent. Try login manually. And send cookies again.");
                changeTempStatus("[not all cookies were sent]", "#ff7137");
            }
        });
    }
}