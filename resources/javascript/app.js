 
function hasClass(element, className) {
    return (' ' + element.className + ' ').indexOf(' ' + className+ ' ') > -1;
}

function uncolor_classes(all_classes, list_of_classnames_to_decolor) {
	for (var i = 0; i < all_classes.length; ++i) {
		var item = all_classes[i];
		for (var j = 0; j < list_of_classnames_to_decolor.length; ++j) {
			if(hasClass(item, list_of_classnames_to_decolor[j])) {
				item.className = '';
				//item.innerHTML = 'test_text';
			}
		}
	}
}


function uncolor_class(className_to_decolor) {
	var all_classes = document.getElementsByTagName("th");
	for (var i = 0; i < all_classes.length; ++i) {
		var item = all_classes[i];
		if(hasClass(item, className_to_decolor)) {
			item.className = 'not_'+className_to_decolor;
		} else if(hasClass(item, 'not_'+className_to_decolor)) {
			item.className = className_to_decolor;
			//alert (item.className);
		}

	}
}

//var all_classes = document.getElementsByClassName("alignment_not_found")
//var classes_to_decolor = ['alignment_error', 'alignment_not_found'];


//uncolor_classes(all_classes, classes_to_decolor);

