import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

SES_CLIENT = boto3.client('ses', region_name='eu-west-3')
SENDER = "Luvrane <orders@luvrane.com>"

def get_html_template(
    template_type: str,
    order,
    customer_name="Client",
    confirmation_token: str = None
):
    """
    Retornamos el cuerpo de correo
    """

    # Convertimos a lista para manejar el bucle uniformemente en el HTML
    orders_list = order if isinstance(order, list) else [order]
    
    if len(orders_list) > 0:
        display_id = orders_list[0].id
        total_global = sum(o.total_price for o in orders_list)
        main_order = orders_list[0]
    else:
        raise ValueError("La liste d'ordres est vide")

    # Adaptación de la fecha al horario de Argelia (UTC+1)
    tz_algeria = ZoneInfo("Africa/Algiers")
    
    # Tomamos la fecha de creación del pedido principal (que está en UTC)
    created_at_utc = main_order.created_at
    
    # Nos aseguramos de que Python reconozca que la fecha de la base de datos es UTC si viene sin zona asignada
    if created_at_utc.tzinfo is None:
        created_at_utc = created_at_utc.replace(tzinfo=timezone.utc)
        
    # Convertimos al horario local de Argelia
    created_at_algeria = created_at_utc.astimezone(tz_algeria)
    
    # Formateamos la fecha en un formato limpio (Ejemplo: "16 mai 2026 à 18:01")
    # %d = día, %b = mes abreviado, %Y = año, %H:%M = hora de 24 horas
    order_date_str = created_at_algeria.strftime("%d %b %Y à %H:%M")

    #Color
    brand_color = "#000000"

    subjects = {
        "order_received": f"Confirmez votre commande #{display_id[:8]} - Luvrane",
        "order_confirmed": "Bonne nouvelle ! Votre commande a été confirmée",
        "order_shipped": "Votre colis est en route !",
        "order_cancelled": "Mise à jour : Commande annulée",
        "new_order_admin": "Nouvelle commande à confirmer"
    }

    # URL dinámica adaptada según el rol del destinatario y el store_id real
    if confirmation_token:
        confirmation_url = f"https://luvrane.com/confirm-order/{confirmation_token}"
    elif template_type == "new_order_admin":
        confirmation_url = f"https://luvrane.com/admin/stores/{main_order.store_id}/orders"
    else:
        confirmation_url = "https://luvrane.com/account/orders"

    # Texto dinámico botón adaptado para el administrador de la tienda
    if confirmation_token:
        button_text = "Confirmer ma commande"
    elif template_type == "new_order_admin":
        button_text = "Gérer les commandes"
    else:
        button_text = "Voir ma commande"

    # Contenido según el tipo
    if template_type == "order_received":

        title = "Confirmez votre commande"

        message = """
        Merci pour votre commande.<br><br>

        Afin de valider définitivement votre achat,
        veuillez confirmer votre commande en cliquant
        sur le bouton ci-dessous.
        """

    elif template_type == "order_confirmed":

        title = "Commande Confirmée"

        message = """
        Votre commande a été confirmée avec succès
        et est actuellement en préparation.
        """

    elif template_type == "order_shipped":

        title = "Votre commande est en route !"

        message = f"""
        Votre colis a été expédié.<br><br>

        Numéro de suivi :
        <b>
            {
                main_order.tracking_number
                if main_order.tracking_number
                else 'Disponible prochainement'
            }
        </b>
        """

    elif template_type == "order_cancelled":

        title = "Commande Annulée"

        message = """
        Votre commande a été annulée.
        Si vous pensez qu'il s'agit d'une erreur,
        vauillez contacter notre support.
        """

    elif template_type == "new_order_admin":

        title = "Nouvelle commande reçue"

        message = """
        Une nouvelle commande vient d'être passée
        sur votre boutique et attend confirmation.
        """

    else:

        title = "Mise à jour de votre commande"

        message = f"""
        Le statut de votre commande
        #{display_id[:8]} a été mis à jour.
        """

    # GENERAMOS EL DESGLOSE DINÁMICO DE TIENDAS Y PRODUCTOS EN HTML
    orders_html_details = ""
    for index, o in enumerate(orders_list, 1):
        orders_html_details += f"""
        <div style="border-bottom: 1px dashed #eee; padding-bottom: 15px; margin-bottom: 15px;">
            <p style="margin: 0 0 10px 0; font-size: 14px; color: #555; font-weight: bold;">
                Colis {index} - Magasin {str(o.store_name)}
            </p>
        """
        
        # Iteramos por las relaciones de tu base de datos (Order.items)
        for item in o.items:
            img_url = None
            
            # 1. Intentamos extraer la primera imagen de la variante (tabla variant_media)
            if item.variant and item.variant.images:
                # Buscamos la imagen en la posición 0 u ordenadas por el atributo 'position'
                sorted_variant_imgs = sorted(item.variant.images, key=lambda x: x.position or 0)
                if sorted_variant_imgs:
                    img_url = sorted_variant_imgs[0].media_url
            
            # 2. Si no hay imagen de variante, buscamos la primera imagen del producto principal (tabla product_images)
            if not img_url and item.product and item.product.images:
                sorted_product_imgs = sorted(item.product.images, key=lambda x: x.position or 0)
                if sorted_product_imgs:
                    img_url = sorted_product_imgs[0].image_url
            
            # 3. Fallback: Si no hay multimedia asociada, colocamos un marcador de posición
            if not img_url:
                img_url = "https://luvrane.com/placeholder.png"

            # 4. Construcción dinámica del nombre con sus atributos físicos (Color y Talla)
            p_name = getattr(item.product, "name", "Produit")
            variant_details = []
            
            if item.variant:
                if item.variant.color and getattr(item.variant.color, "name", None):
                    variant_details.append(f"Couleur: {item.variant.color.name}")
                if item.variant.size and getattr(item.variant.size, "name", None):
                    variant_details.append(f"Taille: {item.variant.size.name}")
            
            if variant_details:
                p_name += f" ({', '.join(variant_details)})"
            
            orders_html_details += f"""
            <table style="width: 100%; margin-bottom: 10px;">
                <tr>
                    <td style="width: 60px; vertical-align: middle;">
                        <img src="{img_url}" alt="{p_name}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px; border: 1px solid #eee;">
                    </td>
                    <td style="vertical-align: middle; padding-left: 10px;">
                        <p style="margin: 0; font-size: 14px; font-weight: bold; color: #333;">{p_name}</p>
                        <p style="margin: 0; font-size: 12px; color: #777;">Qté: {item.quantity} x {item.unit_price} DA</p>
                    </td>
                    <td style="vertical-align: middle; text-align: right; font-size: 14px; font-weight: bold; color: #333;">
                        {item.total_price} DA
                    </td>
                </tr>
            </table>
            """
            
        # Obtenemos la columna shipping_price definida en tu modelo de Order
        orders_html_details += f"""
            <div style="text-align: right; font-size: 13px; color: #666; margin-top: 5px;">
                Frais de livraison de ce magasin: <b>{o.shipping_price} DA</b>
            </div>
        </div>
        """

    html_content = f"""
    <html>

    <body style="
        font-family: Arial, sans-serif;
        color: #333;
        line-height: 1.6;
        background-color: #f5f5f5;
        padding: 20px;
    ">

        <div style="
            max-width: 600px;
            margin: 0 auto;
            background-color: white;
            border: 1px solid #eee;
            padding: 30px;
            border-radius: 10px;
        ">

            <h1 style="
                color: {brand_color};
                text-align: center;
                letter-spacing: 2px;
            ">
                LUVRANE
            </h1>

            <hr style="
                border: 0;
                border-top: 1px solid #eee;
                margin: 20px 0;
            ">

            <h2 style="color: #444;">
                {title}
            </h2>

            <p>
                Bonjour {customer_name},
            </p>

            <p>
                {message}
            </p>

            <div style="
                background-color: #f9f9f9;
                padding: 15px;
                border-radius: 8px;
                margin-top: 20px;
            ">

                <p style="margin-top: 0;">
                    <b>Détails de la commande (Faite le {order_date_str}) :</b>
                </p>

                {orders_html_details}

                <table style="width: 100%; margin-top: 15px; border-top: 1px solid #ddd; padding-top: 10px;">
                    <tr>
                        <td style="font-size: 16px; font-weight: bold; color: #333;">Montant Total Global :</td>
                        <td style="text-align: right; font-size: 18px; font-weight: bold; color: {brand_color};">
                            {total_global} DA
                        </td>
                    </tr>
                </table>

            </div>

            <p style="
                margin-top: 30px;
                text-align: center;
            ">

                <a
                    href="{confirmation_url}"
                    style="
                        background-color: {brand_color};
                        color: white;
                        padding: 14px 24px;
                        text-decoration: none;
                        border-radius: 6px;
                        font-weight: bold;
                        display: inline-block;
                    "
                >
                    {button_text}
                </a>

            </p>

            <hr style="
                border: 0;
                border-top: 1px solid #eee;
                margin-top: 40px;
            ">

            <p style="
                font-size: 12px;
                color: #999;
                text-align: center;
            ">

                Ceci est un message automatique,
                merci de ne pas y répondre.

                <br><br>

                &copy; 2026 Luvrane.
                Tous droits réservés.

            </p>

        </div>

    </body>

    </html>
    """

    return subjects.get(
        template_type,
        "Mise à jour Luvrane"
    ), html_content


def send_order_email(
    to_email: str,
    template_type: str,
    order,
    customer_name="Client",
    confirmation_token: str = None
):
    try:
        subject, body_html = get_html_template(
            template_type,
            order,
            customer_name,
            confirmation_token
        )

        clean_order = order[0] if isinstance(order, list) else order

        SES_CLIENT.send_email(

            Source=SENDER,

            Destination={
                'ToAddresses': [to_email]
            },

            Message={

                'Subject': {
                    'Data': subject
                },

                'Body': {

                    'Html': {
                        'Data': body_html
                    },

                    'Text': {
                        'Data': (
                            f"Commande #{clean_order.id[:8]} - "
                            f"Visitez Luvrane pour plus de détails."
                        )
                    }
                }
            }
        )

    except ClientError as e:

        print(
            f"Erreur SES: "
            f"{e.response['Error']['Message']}"
        )
    except Exception as general_err:
        print(f"Erreur interne lors de l'envoi de l'email: {str(general_err)}")