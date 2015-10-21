$(document).keydown(function(e) {
    var keycode = e.which || e.keyCode;
    var key = String.fromCharCode(keycode).toLowerCase()

    {% if user.is_authenticated %}
    if (key == 'e' && e.ctrlKey)
    {
        location.href='{% url 'edit_page' page %}';
        e.preventDefault();
    }
    {% endif %}
    if (key == 'p' && e.ctrlKey)
    {
        /* window.print() */
        location.href='{% url 'ppdf_page' page %}';
        e.preventDefault();
    }
    if (key == 'l' && e.ctrlKey)
    {
        {% if user.is_authenticated %}
        location.href='{% url 'core_logout' %}?next={% url 'show_page' page %}';
        {% else %}
        location.href='{% url 'core_login' %}?next={% url 'show_page' page %}';
        {% endif %}
        e.preventDefault();
    }
    if (key == 'i' && e.ctrlKey)
    {
        location.href='{% url 'core_index' %}';
        e.preventDefault();
    }
    if (key == 'q' && e.ctrlKey)
    {
        /* $("header").toggle(); */
        location.href='{% url 'show_full' page %}';
        e.preventDefault();
    }

    // 37 left 38 up 39 right 40 down 
    // 188 comma 190 period 191 forward slash

    {% if page.parent.parent %}    
    if (e.ctrlKey && keycode == '38')
    {
        location.href='{% url 'show_page' page.parent %}';
        e.preventDefault();
    }
    {% endif %}

    {% if page.prev %}
    if (keycode == '37')
    {
        location.href='{% url 'show_page' page.prev %}';
        e.preventDefault();
    }
    {% endif %}

    {% if page.next %}
    if (keycode == '39')
    {
        location.href='{% url 'show_page' page.next %}';
        e.preventDefault();
    }
    {% endif %}

    {% if page.down_list %}
    if (e.ctrlKey && keycode == '40')
    {
        location.href='{% url 'show_page' page.down_list.0 %}';
        e.preventDefault();
    }
    {% endif %}

    {% if user.is_staff %}    
    if (keycode == '191')
    {
        location.href='{% url 'root_page' %}';
        e.preventDefault();
    }
    {% endif %}
    
});
