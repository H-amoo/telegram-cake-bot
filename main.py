from telegram import ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

from config import TOKEN
from cakes import cakes

ASK_NAME, ASK_CAKE, ASK_PHONE = range(3)


async def start(update, context):
    keyboard = [
        ["منوی کیک ها"],
        ["سفارش"],
        ["آدرس"],
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "به قنادی ما خوش آمدید 🍰",
        reply_markup=markup,
    )


async def menu(update, context):
    text = "منوی کیک‌ها:\n\n"

    for cake_name, price in cakes.items():
        text += f"{cake_name} : {price:,} تومان\n"

    await update.message.reply_text(text)


async def address(update, context):
    await update.message.reply_text(
        "آدرس: تهران - خیابان نمونه - پلاک ۱۰"
    )


async def order_start(update, context):
    await update.message.reply_text(
        "لطفاً نام خود را وارد کنید:"
    )
    return ASK_NAME


async def get_name(update, context):
    context.user_data["name"] = update.message.text

    await update.message.reply_text(
        "چه کیکی می‌خواهید؟\n\n" + "\n".join(cakes.keys())
    )

    return ASK_CAKE


async def get_cake(update, context):
    context.user_data["cake"] = update.message.text

    await update.message.reply_text(
        "شماره تماس خود را وارد کنید:"
    )

    return ASK_PHONE


async def get_phone(update, context):
    context.user_data["phone"] = update.message.text

    name = context.user_data["name"]
    cake_name = context.user_data["cake"]
    phone = context.user_data["phone"]

    summary = (
        "سفارش شما ثبت شد ✅\n\n"
        f"نام: {name}\n"
        f"کیک: {cake_name}\n"
        f"شماره تماس: {phone}"
    )

    await update.message.reply_text(summary)

    context.user_data.clear()

    return ConversationHandler.END


async def cancel(update, context):
    context.user_data.clear()

    await update.message.reply_text(
        "سفارش لغو شد."
    )

    return ConversationHandler.END


async def keyboard(update, context):
    text = update.message.text

    if text == "منوی کیک ها":
        await menu(update, context)

    elif text == "سفارش":
        return await order_start(update, context)

    elif text == "آدرس":
        await address(update, context)


app = Application.builder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex("^سفارش$"), order_start)
    ],
    states={
        ASK_NAME: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                get_name,
            )
        ],
        ASK_CAKE: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                get_cake,
            )
        ],
        ASK_PHONE: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                get_phone,
            )
        ],
    },
    fallbacks=[
        CommandHandler("cancel", cancel)
    ],
)

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("menu", menu))
app.add_handler(conv_handler)
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        keyboard,
    )
)

app.run_polling()