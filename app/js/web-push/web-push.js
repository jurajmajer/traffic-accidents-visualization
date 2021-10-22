'use strict';

const applicationServerPublicKey = "BCuBmxX3n1-uVqdCECymi1G4s0nhM4d5XsEJMy0KhSrUxeBjIebw4P29g54DoZUHJ_0ax5As6GhdurEGLI9h13w"
var pushButton = null
let isSubscribed = false
var counties = {"Banskobystrický kraj" : 6, "Bratislavský kraj" : 1, "Košický kraj" : 8, "Nitriansky kraj" : 4, "Prešovský kraj" : 7, "Trenčiansky kraj" : 3, "Trnavský kraj" : 2, "Žilinský kraj" : 5}
var districts = {"Bratislava I" : 101, "Bratislava II" : 102, "Bratislava III" : 103, "Bratislava IV" : 104, "Bratislava V" : 105, "Malacky" : 106, "Pezinok" : 107, "Senec" : 108, "Dunajská Streda" : 201, "Galanta" : 202, "Hlohovec" : 203, "Piešťany" : 204, "Senica" : 205, "Skalica" : 206, "Trnava" : 207, "Bánovce nad Bebravou" : 301, "Ilava" : 302, "Myjava" : 303, "Nové Mesto nad Váhom" : 304, "Partizánske" : 305, "Trenčín" : 309, "Komárno" : 401, "Levice" : 402, "Nitra" : 403, "Nové Zámky" : 404, "Šaľa" : 405, "Topoľčany" : 406, "Zlaté Moravce" : 407, "Čadca" : 502, "Dolný Kubín" : 503, "Liptovský Mikuláš" : 505, "Martin" : 506, "Ružomberok" : 508, "Turčianske Teplice" : 509, "Žilina" : 511, "Banská Bystrica" : 601, "Brezno" : 603, "Detva" : 604, "Lučenec" : 606, "Revúca" : 608, "Rimavská Sobota" : 609, "Žarnovica" : 612, "Žiar nad Hronom" : 613, "Bardejov" : 701, "Humenné" : 702, "Kežmarok" : 703, "Levoča" : 704, "Medzilaborce" : 705, "Poprad" : 706, "Prešov" : 707, "Snina" : 709, "Stará Ľubovňa" : 710, "Vranov nad Topľou" : 713, "Košice I" : 802, "Košice II" : 803, "Košice III" : 804, "Košice IV" : 805, "Košice - okolie" : 806, "Michalovce" : 807, "Rožňava" : 808, "Spišská Nová Ves" : 810, "Trebišov" : 811, "Považská Bystrica" : 306, "Námestovo" : 507, "Banská Štiavnica" : 602, "Veľký Krtíš" : 610, "Zvolen" : 611, "Prievidza" : 307, "Kysucké Nové Mesto" : 504, "Púchov" : 308, "Svidník" : 712, "Gelnica" : 801, "Krupina" : 605, "Tvrdošín" : 510, "Sabinov" : 708, "Bytča" : 501, "Stropkov" : 711, "Sobrance" : 809, "Poltár" : 607}

function urlB64ToUint8Array(base64String) {
	const padding = '='.repeat((4 - base64String.length % 4) % 4);
	const base64 = (base64String + padding)
		.replace(/\-/g, '+')
		.replace(/_/g, '/');

	const rawData = window.atob(base64);
	const outputArray = new Uint8Array(rawData.length);

	for (let i = 0; i < rawData.length; ++i) {
		outputArray[i] = rawData.charCodeAt(i);
	}
	return outputArray;
}

function updateSubscriptionOnServer(url, data) {
	fetch(url, {
        method: 'post',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });
}

function subscribeUser() {
	window.Notification.requestPermission().then(function (permission) {
		// TODO: Provide feedback in case permission is not granted; this can happen if the user revoked the permission
		// after having subscribed once, and in that case, the only way to regrant permission in e.g. Firefox and
		// Chrome on Android is through the user agent's settings; that's poor UX.
		if (permission === 'granted') {
			// Use the VAPID keys generated out of band. The corresponding private key will be used by the service
			// responsible for actually pushing messages.
			var applicationServerKey = urlB64ToUint8Array(applicationServerPublicKey)
			var options = { applicationServerKey: applicationServerKey, userVisibleOnly: true }
			navigator.serviceWorker.ready.then(function(reg) {
				reg.pushManager.subscribe(options).then(function(subscription) {
    				setButtonText()
					updateSubscriptionOnServer('/api/web-push/save-subscription', getSubscribeData(subscription))
				}).catch(function(e) {
					displayError("Nastala chyba pri registrovaní notifikácií: " + e)
				})
			})
		} else {
    		displayError("Nepodarilo sa získať oprávnenie vo vašom prehliadači na zasielanie notifikácií. Skúste manuálne povoliť notifikácie pre našu doménu v nastaveniach vášho prehliadača.")
			pushButton.disabled = true;
		}
	})
}

function getSubscribeData(subscription) {
    return {
        "token" : subscription,
        "weekdays" : [$("#monday").is(':checked'), $("#tuesday").is(':checked'), $("#wednesday").is(':checked'), $("#thursday").is(':checked'), $("#friday").is(':checked'), $("#saturday").is(':checked'), $("#sunday").is(':checked')],
        "from_time" : $("#from_time").val(),
        "to_time" : $("#to_time").val(),
        "counties" : getCountyList(),
        "districts" : getDistrictList()
    }
}

function getCountyList() {
    if($("#county").is(':checked')) {
        return getItemsFromList("county-list", counties);
    }
    return []
}

function getDistrictList() {
    if($("#district").is(':checked')) {
        return getItemsFromList("district-list", districts);
    }
    return []
}

function getItemsFromList(ulId, lookUpDict) {
    var retVal = [];
    var keys = Object.keys(lookUpDict)
    $("#"+ulId+" > li > span.web-notification-list-item-value").each(function( index ) {
      if(keys.includes($( this ).text()))
          retVal.push(lookUpDict[$( this ).text()]);
    });
    return retVal;
}

function unsubscribeUser() {
	navigator.serviceWorker.ready.then(function(reg) {
		reg.pushManager.getSubscription().then(function(subscription) {
			if (subscription) {
				subscription.unsubscribe().then(function(successful) {
    				setButtonText()
					updateSubscriptionOnServer('/api/web-push/remove-subscription', getUnsubscribeData(subscription))
				}).catch(function(e) {
					displayError("Nastala chyba pri odregistrovaní notifikácií: " + e)
				})
			}
		})        
	});
}

function getUnsubscribeData(subscription) {
    return {
        "token" : subscription
    }
}

function setButtonText() {
	if (isSubscribed) {
    	$("#notification-input-data").hide()
    	$("#msg-div").show()
		pushButton.textContent = 'Odregistrovať notifikácie'
	}
	else {
    	$("#notification-input-data").show()
    	$("#msg-div").hide()
		pushButton.textContent = 'Zaregistrovať notifikácie'
	}
}

function initializeUI(swRegistration) {
	pushButton.addEventListener('click', function() {
		isSubscribed = !isSubscribed
		if (isSubscribed) {
			subscribeUser()
		} else {
			unsubscribeUser()
		}
	});
	
	swRegistration.pushManager.getSubscription().then(function(subscription) {
		isSubscribed = !(subscription === null);
		setButtonText();
	});
	
	populateUI()
	$('input:radio[name="locality"]').change(function(){
    	hideLocalityItems()
    	var id = "#" + $(this).val() + "-select-div"
    	$(id).show()
    	id = "#" + $(this).val() + "-list"
    	$(id).show()
	});
}

function populateUI() {
    autocomplete(document.getElementById("county-select"), Object.keys(counties));
    $("#county-select").on("change", function() {
        addItemToList("county-list", $("#county-select"), Object.keys(counties));
    });
    autocomplete(document.getElementById("district-select"), Object.keys(districts));
    $("#district-select").on("change", function() {
        addItemToList("district-list", $("#district-select"), Object.keys(districts));
    });
    hideLocalityItems()
}

function addItemToList(ulId, elWithValue, possibleValues) {
    var text = elWithValue.val()
    if (!possibleValues.includes(text))
        return;
    if($("#"+ulId+" > li").text().indexOf(text + "x") !== -1)
        return;
    $("#"+ulId).append("<li class='web-notification-list-item'><span class='web-notification-list-item-value'>"+text+"</span><span class='web-notification-list-item' onclick='removeItemFromList(this)'>x</span></li>");
    text = elWithValue.val("")
}

function removeItemFromList(el) {
    el.parentElement.remove();
}

function hideLocalityItems() {
    $("#county-select-div").hide()
    $("#county-list").hide()
    $("#district-select-div").hide()
    $("#district-list").hide()
}

function displayError(errorMsg) {
    $("#error-msg").text(errorMsg)
    $("#error-msg-div").show()
}

$(document).ready(function(){
    $("#error-msg-div").hide()
    pushButton = document.querySelector('.web-notification-push-btn')
	if (navigator && navigator.serviceWorker && 'PushManager' in window) {
        navigator.serviceWorker.register('/sw.js').then(function(swRegistration) {
			initializeUI(swRegistration);
		})
		.catch(function(error) {
			displayError("Nastala chyba pri registrácii sw.js: " + error)
		});
    } else {
        displayError("Váš prehliadač nepodporuje možnosť zasielania notifikácií. Skúste iný prehliadač.")
		pushButton.disabled = true;
	}
});
