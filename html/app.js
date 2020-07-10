
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


function uncheck_class(flag, cl_id) {
	var className = "check_" + flag;
	var checkboxclassName = "checkbox_" + flag;
	var bool_val = document.getElementById(cl_id).checked;
	alert(bool_val);
	var all_classes = document.getElementsByTagName("th");
	for (var i = 0; i < all_classes.length; ++i) {
		var item = all_classes[i];
		if(hasClass(item, className) == true) {
			var class_checkbox = item.getElementsByTagName("input")[0];
			var individual_checkbox = all_classes[i-3].getElementsByTagName("input")[0]
			if(class_checkbox.checked == true){
				class_checkbox.checked = true;
				individual_checkbox.checked = true;
				$( class_checkbox ).prop('checked', true);
				// $( individual_checkbox ).prop('checked', false);

				// $("."+className).click(function () {
				// 	alert("0000000");
				// 	if (this.checked==true){
				// 		alert("lalala");
				// 	}
				// 	else {
				// 		alert('lololol')
				// 	}
				// });
			}

			else {
				class_checkbox.checked = false;
				individual_checkbox.checked = false;
				$( class_checkbox ).prop('checked', false);
			}


			// $("."+className).change(function () {
			// 	debugger;
			// 	if (this.checked) {
			// 		alert("3333333");
			// 		$("."+className).prop("checked", false);
			// 		alert("444444");
			// 	}
			// 	else {
			// 		//opposite of that in if - block
			// 	}

			// });


			//$(class_checkbox).prop("checked", class_checkbox.checked);
			//$("."+checkboxclassName).prop("checked", individual_checkbox.checked);
		}
	}
}


function change_value(id){
	if(document.getElementById(id).value == "0") {
		document.getElementById(id).value = "1";
	}
	else {
		document.getElementById(id).value = "0";
	}    
}


function save_to_file(path, data){
	file = fopen(getScriptPath(), 3);
	if(file!=-1) // If the file has been successfully opened
	{
	    fwrite(file, data);
	}
}


function to_tmx(){	
	var data_array = [];
	var all_rows = document.getElementsByTagName("tr");
	// get the languages
	var lang_row = all_rows[1];
	var lang_cells = lang_row.getElementsByTagName("th");
	var lang_src = lang_cells[1].textContent.toLowerCase();
	var lang_trgt = lang_cells[2].textContent.toLowerCase();
	//get the index for all checked checkboxes
	for (var i = 2; i < all_rows.length; ++i) {
		var row = all_rows[i];
		var cells = row.getElementsByTagName("th");
		var checkbox = cells[0].getElementsByTagName("input")[0];
		if(checkbox.value == "1"){
			data_array.push(i);
		}
	}
	var data = '<tmx version="1.4b">\n  <header\n    creationtool="RALIYasaAligner" creationtoolversion="0.1"\n    datatype="PlainText" segtype="phrase"\n    adminlang="en-US" srclang="' + lang_src + '"\n    o-tmf="TMX"/>\n  <body>\n';
	// call a python script to retrieve the checked sentences
	for (var i = 0; i < data_array.length; i++) {
		// get the different information for the tmx
		var j = data_array[i];
		var row = all_rows[j];
		var cells = row.getElementsByTagName("th");
		var src_sent = cells[1].textContent;
		var trgt_sent = cells[2].textContent;
		var flag = cells[3].textContent;
		var d = new Date();
		// add the info to the tmx data variable
		var data = data.concat('    <tu flag="true" flag_date="'+d.getFullYear()+'-'+d.getMonth()+'-'+d.getDate()+' '+d.getHours()+':'+d.getMinutes()+':'+d.getSeconds());
		var data = data.concat('" flag_type="HUMAN CHECKED ('+flag+')>\n      <tuv xml:lang="'+lang_src+'">\n        <seg><![CDATA['+src_sent+']]></seg>\n      </tuv>\n');
		var data = data.concat('      <tuv xml:lang="'+lang_trgt+'">\n        <seg><![CDATA['+trgt_sent+']]></seg>\n      </tuv>\n    </tu>\n');
	}
	// and make the tmx
	var data = data.concat('  </body>\n</tmx>');
	var data = "data:text/xml;charset=utf-8," + data
	var encoded = encodeURI(data);
	var link = document.createElement("a");
	link.setAttribute("href", encoded);
	link.setAttribute("download", "translation_memory.tmx");
	document.body.appendChild(link);
	// download when clicked on
	link.click();
}
