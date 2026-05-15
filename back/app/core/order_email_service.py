import boto3
from botocore.exceptions import ClientError

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

    # Si es una lista de órdenes (como en checkout_service), extraemos la primera para el template
    if isinstance(order, list):
        if len(order) > 0:
            order = order[0]
        else:
            raise ValueError("La liste d'ordres est vide")

    #Color
    brand_color = "#000000"

    subjects = {
        "order_received": f"Confirmez votre commande #{order.id[:8]} - Luvrane",
        "order_confirmed": "Bonne nouvelle ! Votre commande a été confirmée",
        "order_shipped": "Votre colis est en route !",
        "order_cancelled": "Mise à jour : Commande annulée",
        "new_order_admin": "Nouvelle commande à confirmer"
    }

    # URL dinámica
    confirmation_url = (
        f"https://luvrane.com/confirm-order/{confirmation_token}"
        if confirmation_token
        else "https://luvrane.com/account/orders"
    )

    # Texto dinámico botón
    button_text = (
        "Confirmer ma commande"
        if confirmation_token
        else "Voir ma commande"
    )

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
                order.tracking_number
                if order.tracking_number
                else 'Disponible prochainement'
            }
        </b>
        """

    elif template_type == "order_cancelled":

        title = "Commande Annulée"

        message = """
        Votre commande a été annulée.
        Si vous pensez qu'il s'agit d'une erreur,
        veuillez contacter notre support.
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
        #{order.id[:8]} a été mis à jour.
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

                <p>
                    <b>Résumé de la commande :</b>
                </p>

                <p>
                    ID : #{order.id[:8]}
                </p>

                <p>
                    Total :
                    <b>{order.total_price} DA</b>
                </p>

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

        # Ajustamos también el texto plano por si viene una lista de órdenes
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