import json
import os
import time
import uuid

import streamlit as st
from llm_agent import ConversationAgent


CONVERSATIONS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "conversations.json")


# Historique des conversations : sauvegardé dans un fichier JSON
# pour survivre au rechargement de la page et au redémarrage de l'app
def load_conversations():
	if not os.path.exists(CONVERSATIONS_PATH):
		return {}
	with open(CONVERSATIONS_PATH, "r", encoding="utf-8") as file:
		return json.load(file)


def save_conversations(conversations):
	with open(CONVERSATIONS_PATH, "w", encoding="utf-8") as file:
		json.dump(conversations, file, ensure_ascii=False, indent=2)


def make_title(text, max_length=35):
	text = text.strip().replace("\n", " ")
	return text if len(text) <= max_length else text[:max_length] + "…"


st.set_page_config(page_title="Jarvis")
st.title("Barbe-Quasar")


# Streamlit relance le script à chaque message,
# seul st.session_state survit entre deux interactions
if "conversations" not in st.session_state:
	st.session_state.conversations = load_conversations()

# L'agent garde la mémoire de la conversation en cours ;
# current_id = None tant que la nouvelle conversation n'a pas commencé
if "agent" not in st.session_state:
	st.session_state.agent = ConversationAgent()
	st.session_state.current_id = None

conversations = st.session_state.conversations
agent = st.session_state.agent


with st.sidebar:
	if st.button("➕ Nouvelle conversation", use_container_width=True):
		st.session_state.agent = ConversationAgent()
		st.session_state.current_id = None
		st.rerun()

	st.subheader("Historique")

	if not conversations:
		st.caption("Aucune conversation pour l'instant.")

	# Les plus récentes en premier
	sorted_conversations = sorted(
		conversations.items(),
		key=lambda item: item[1]["updated_at"],
		reverse=True,
	)
	for conversation_id, conversation in sorted_conversations:
		is_current = conversation_id == st.session_state.current_id
		if st.button(
			conversation["title"],
			key=conversation_id,
			type="primary" if is_current else "secondary",
			use_container_width=True,
		):
			# L'agent reprend la mémoire de la conversation choisie
			st.session_state.agent = ConversationAgent(conversation["messages"])
			st.session_state.current_id = conversation_id
			st.rerun()


# Réaffiche les messages de la conversation en cours
for message in agent.conversation_history:
	with st.chat_message(message["role"]):
		st.markdown(message["content"])


user_input = st.chat_input(
	"Que veux tu moussaillon ?",
	accept_file=False,
	)

if user_input :
	with st.chat_message("user"):
		st.markdown(user_input)

	with st.chat_message("assistant"):
		with st.spinner("Barbe-Quasar réfléchit..."):
			response = agent.ask_llm(user_input)
		st.markdown(response)

	# Première question : on ajoute la conversation à l'historique
	# (même liste que la mémoire de l'agent, elle se met à jour toute seule)
	if st.session_state.current_id is None:
		st.session_state.current_id = str(uuid.uuid4())
		conversations[st.session_state.current_id] = {
			"title": make_title(user_input),
			"messages": agent.conversation_history,
		}

	conversations[st.session_state.current_id]["updated_at"] = time.time()
	save_conversations(conversations)

	# Relance pour mettre à jour la barre latérale
	st.rerun()
